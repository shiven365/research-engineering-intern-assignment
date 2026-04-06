from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

import faiss
import numpy as np
import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from data.database import get_connection
from data.loader import load_to_duckdb
from llm.chatbot import chat as llm_chat
from llm.summarizer import generate_timeseries_summary
from ml.clustering import cluster_posts
from ml.embeddings import build_index, load_index, semantic_search
from ml.network import build_subreddit_network, graph_to_json


DATA_PATH = os.getenv("DATA_PATH", str(Path(__file__).resolve().parent / "data.jsonl"))

app = FastAPI(title="NarrativeScope API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATE: dict[str, Any] = {
    "conn": None,
    "df": None,
    "index": None,
    "id_map": None,
    "embedding_matrix": None,
}


def _safe_response(data: Any = None, error: Optional[str] = None, **extra: Any) -> dict[str, Any]:
    return {"data": data, "error": error, **extra}


def _load_dataframe(conn) -> pd.DataFrame:
    return conn.execute("SELECT * FROM posts").df()


def _filter_df(
    df: pd.DataFrame,
    subreddit: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    out = df
    if subreddit:
        out = out[out["subreddit"] == subreddit]

    if start_date or end_date:
        with_dates = out.assign(_date_filter=pd.to_datetime(out["date_only"], errors="coerce").dt.date)

        if start_date:
            start = pd.to_datetime(start_date, errors="coerce")
            if pd.notnull(start):
                with_dates = with_dates[with_dates["_date_filter"] >= start.date()]

        if end_date:
            end = pd.to_datetime(end_date, errors="coerce")
            if pd.notnull(end):
                with_dates = with_dates[with_dates["_date_filter"] <= end.date()]

        out = with_dates.drop(columns=["_date_filter"])

    return out


def _serialize_posts(df: pd.DataFrame) -> list[dict[str, Any]]:
    cols = [
        "id",
        "title",
        "selftext",
        "text_combined",
        "author",
        "subreddit",
        "score",
        "num_comments",
        "num_crossposts",
        "engagement_score",
        "created_dt",
        "date_only",
        "url",
        "permalink",
        "domain",
    ]
    rows = []
    for _, row in df[cols].iterrows():
        rows.append(
            {
                "id": row["id"],
                "title": row["title"],
                "text": row["text_combined"],
                "author": row["author"],
                "subreddit": row["subreddit"],
                "score": int(row["score"] or 0),
                "num_comments": int(row["num_comments"] or 0),
                "num_crossposts": int(row["num_crossposts"] or 0),
                "engagement_score": int(row["engagement_score"] or 0),
                "created_dt": row["created_dt"].isoformat() if pd.notnull(row["created_dt"]) else None,
                "date_only": row["date_only"].isoformat() if pd.notnull(row["date_only"]) else None,
                "url": row["url"],
                "permalink": row["permalink"],
                "domain": row["domain"],
            }
        )
    return rows


@app.on_event("startup")
async def startup() -> None:
    conn = get_connection()
    try:
        has_posts = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0] > 0
    except Exception:
        has_posts = False

    if not has_posts:
        load_to_duckdb(DATA_PATH)

    df = _load_dataframe(conn)
    STATE["conn"] = conn
    STATE["df"] = df

    try:
        index, id_map = load_index()
        if index is None or id_map is None:
            texts = df["text_combined"].fillna("").tolist()
            post_ids = df["id"].tolist()
            index, id_map, embedding_matrix = build_index(texts, post_ids)
            STATE["embedding_matrix"] = embedding_matrix
        else:
            STATE["embedding_matrix"] = None

        STATE["index"] = index
        STATE["id_map"] = id_map
    except Exception:
        # Keep API online even if embedding stack is unavailable.
        STATE["index"] = None
        STATE["id_map"] = []
        STATE["embedding_matrix"] = None


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/stats/overview")
async def overview():
    try:
        df = STATE["df"]
        if df is None or df.empty:
            return _safe_response(
                {
                    "total_posts": 0,
                    "unique_authors": 0,
                    "unique_subreddits": 0,
                    "date_range": {"start": None, "end": None},
                    "top_subreddits": [],
                }
            )

        top_subs = (
            df.groupby("subreddit")
            .size()
            .sort_values(ascending=False)
            .head(10)
            .reset_index(name="post_count")
            .to_dict("records")
        )

        payload = {
            "total_posts": int(len(df)),
            "unique_authors": int(df["author"].nunique()),
            "unique_subreddits": int(df["subreddit"].nunique()),
            "date_range": {
                "start": df["created_dt"].min().isoformat() if pd.notnull(df["created_dt"].min()) else None,
                "end": df["created_dt"].max().isoformat() if pd.notnull(df["created_dt"].max()) else None,
            },
            "top_subreddits": top_subs,
        }
        return _safe_response(payload)
    except Exception as e:
        return _safe_response(None, str(e))


@app.get("/api/timeseries")
async def timeseries(
    metric: str = Query("post_count", pattern="^(post_count|avg_score|engagement)$"),
    subreddit: Optional[str] = None,
    granularity: str = Query("day", pattern="^(hour|day|week)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    try:
        df = _filter_df(STATE["df"], subreddit, start_date, end_date)
        if df.empty:
            return _safe_response({"series": [], "summary": "No data found for selected filters."})

        df = df.copy()
        if granularity == "hour":
            df["bucket"] = pd.to_datetime(df["created_dt"]).dt.floor("h")
        elif granularity == "week":
            df["bucket"] = pd.to_datetime(df["created_dt"]).dt.to_period("W").dt.start_time
        else:
            df["bucket"] = pd.to_datetime(df["created_dt"]).dt.date

        if metric == "avg_score":
            series_df = df.groupby("bucket", as_index=False)["score"].mean().rename(columns={"score": "value"})
        elif metric == "engagement":
            series_df = (
                df.groupby("bucket", as_index=False)["engagement_score"].mean().rename(columns={"engagement_score": "value"})
            )
        else:
            series_df = df.groupby("bucket", as_index=False).size().rename(columns={"size": "value"})

        series_df = series_df.sort_values("bucket")
        values = series_df["value"].tolist()
        trend = "stable"
        if len(values) > 1:
            slope = values[-1] - values[0]
            if slope > 0:
                trend = "increasing"
            elif slope < 0:
                trend = "decreasing"

        peak_idx = int(np.argmax(values)) if values else 0
        top_subreddits = (
            df.groupby("subreddit").size().sort_values(ascending=False).head(3).index.tolist()
        )

        summary_input = {
            "metric": metric,
            "date_range": {
                "start": str(series_df["bucket"].iloc[0]) if len(series_df) else None,
                "end": str(series_df["bucket"].iloc[-1]) if len(series_df) else None,
            },
            "total": int(np.sum(values)) if metric == "post_count" else int(len(df)),
            "peak_date": str(series_df["bucket"].iloc[peak_idx]) if len(series_df) else None,
            "peak_value": float(values[peak_idx]) if values else 0.0,
            "trend": trend,
            "top_subreddits": top_subreddits,
            "avg_value": float(np.mean(values)) if values else 0.0,
            "data_points": int(len(series_df)),
        }

        try:
            ai_summary = generate_timeseries_summary(summary_input)
        except Exception:
            ai_summary = "AI summary unavailable. Showing numeric trend only."

        series_payload = [
            {"timestamp": str(row["bucket"]), "value": float(row["value"])}
            for _, row in series_df.iterrows()
        ]

        return _safe_response({"series": series_payload, "summary": ai_summary, "meta": summary_input})
    except Exception as e:
        return _safe_response(None, str(e))


@app.get("/api/search")
async def search(
    q: str = Query("", min_length=0),
    k: int = Query(10, ge=1, le=50),
    subreddit: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    try:
        df = _filter_df(STATE["df"], subreddit=subreddit, start_date=start_date, end_date=end_date)
        if df.empty:
            return {
                "results": [],
                "mode": "filtered_empty",
                "message": "No posts found for selected subreddit/date filters.",
                "error": None,
            }

        if not q or len(q.strip()) < 2 or STATE.get("index") is None:
            fallback = df.sort_values("engagement_score", ascending=False).head(k)
            return {
                "results": _serialize_posts(fallback),
                "mode": "fallback_top_engagement",
                "message": "Semantic index unavailable or query too short. Showing top posts by engagement.",
                "error": None,
            }

        candidate_k = min(max(k * 10, 50), max(len(STATE.get("id_map") or []), k))
        matches = semantic_search(q, STATE["index"], STATE["id_map"], k=candidate_k)
        if not matches:
            return {
                "results": [],
                "mode": "semantic",
                "message": "No semantic matches found.",
                "error": None,
            }

        scores = {m["post_id"]: m["similarity_score"] for m in matches}
        match_ids = list(scores.keys())
        result_df = df[df["id"].isin(match_ids)].copy()

        result_df["similarity_score"] = result_df["id"].map(scores)
        result_df = result_df.sort_values("similarity_score", ascending=False)

        rows = _serialize_posts(result_df)
        for r in rows:
            r["similarity_score"] = float(scores.get(r["id"], 0.0))

        return {"results": rows[:k], "mode": "semantic", "message": None, "error": None}
    except Exception as e:
        return {"results": [], "mode": "semantic", "message": None, "error": str(e)}


@app.get("/api/network")
async def network(
    min_edge_weight: int = Query(1, ge=1),
    remove_node: Optional[str] = None,
    centrality_metric: str = Query("pagerank", pattern="^(pagerank|betweenness)$"),
):
    try:
        df = STATE["df"]
        graph = build_subreddit_network(df)
        graph_json = graph_to_json(graph, remove_node=remove_node)

        if min_edge_weight > 1:
            graph_json["edges"] = [e for e in graph_json["edges"] if e["weight"] >= min_edge_weight]

        if not graph_json["edges"] and graph_json["nodes"]:
            graph_json["message"] = "No connections found with current filters"

        graph_json["centrality_metric"] = centrality_metric
        return _safe_response(graph_json)
    except Exception as e:
        return _safe_response(None, str(e))


@app.get("/api/clusters")
async def clusters(
    n_clusters: Optional[int] = Query(None, ge=2, le=100),
    subreddit: Optional[str] = None,
):
    try:
        df = STATE["df"]
        if subreddit:
            df = df[df["subreddit"] == subreddit]

        if df.empty:
            return _safe_response({"coords": [], "labels": [], "cluster_topics": {}, "warnings": ["No data."]})

        if STATE.get("index") is None:
            return _safe_response(
                {
                    "coords": [],
                    "labels": [],
                    "cluster_topics": {},
                    "warnings": ["Embedding index unavailable; clustering disabled."],
                }
            )

        texts = df["text_combined"].fillna("").tolist()
        vectors = STATE["index"].reconstruct_n(0, STATE["index"].ntotal)
        id_to_idx = {pid: i for i, pid in enumerate(STATE["id_map"])}
        selected_idx = [id_to_idx[pid] for pid in df["id"].tolist() if pid in id_to_idx]
        emb = np.array(vectors)[selected_idx]

        result = cluster_posts(emb, texts, n_clusters=n_clusters)
        result["post_ids"] = df["id"].tolist()
        result["titles"] = df["title"].tolist()
        result["subreddits"] = df["subreddit"].tolist()
        return _safe_response(result)
    except Exception as e:
        return _safe_response(None, str(e))


class ChatMessage(BaseModel):
    query: str
    history: list[dict[str, Any]] = []


@app.post("/api/chat")
async def chat(body: ChatMessage):
    try:
        if STATE.get("index") is None:
            return _safe_response(
                {
                    "response": "Semantic retrieval is currently unavailable because embeddings did not initialize.",
                    "retrieved_posts": [],
                }
            )

        search_results = semantic_search(body.query, STATE["index"], STATE["id_map"], k=10)
        df = STATE["df"]
        score_map = {r["post_id"]: r["similarity_score"] for r in search_results}

        if score_map:
            retrieved = df[df["id"].isin(score_map.keys())].copy()
            retrieved["similarity_score"] = retrieved["id"].map(score_map)
            retrieved = retrieved.sort_values("similarity_score", ascending=False)
        else:
            retrieved = pd.DataFrame()

        retrieved_posts = []
        if not retrieved.empty:
            for _, row in retrieved.iterrows():
                retrieved_posts.append(
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "subreddit": row["subreddit"],
                        "text": row["text_combined"],
                        "score": int(row["score"] or 0),
                        "author": row["author"],
                        "created_dt": row["created_dt"].isoformat() if pd.notnull(row["created_dt"]) else None,
                        "url": row["url"],
                        "permalink": row["permalink"],
                        "similarity_score": float(row["similarity_score"] or 0.0),
                    }
                )

        try:
            response_text = llm_chat(body.query, retrieved_posts, body.history)
        except Exception:
            response_text = "I could not reach the language model right now. Try again shortly."

        return _safe_response({"response": response_text, "retrieved_posts": retrieved_posts})
    except Exception as e:
        return _safe_response(None, str(e))


@app.get("/api/subreddits")
async def subreddits():
    try:
        df = STATE["df"]
        subs = (
            df.groupby("subreddit")
            .size()
            .sort_values(ascending=False)
            .reset_index(name="post_count")
            .to_dict("records")
        )
        return _safe_response(subs)
    except Exception as e:
        return _safe_response(None, str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
