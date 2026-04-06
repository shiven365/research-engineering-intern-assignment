"""Shared data loading and resource management for NarrativeScope.
Uses Streamlit caching to avoid reloading on every interaction.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st

# ── Ensure backend is importable ─────────────────────────────────────────────
BACKEND_DIR = str(Path(__file__).resolve().parent / "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(BACKEND_DIR) / ".env")

# Bridge Streamlit Cloud secrets → os.environ
try:
    for key in ["ANTHROPIC_API_KEY"]:
        if key in st.secrets:
            os.environ[key] = st.secrets[key]
except Exception:
    pass


def _resolve_data_path() -> str:
    """Resolve dataset path from env with safe fallbacks."""
    project_root = Path(__file__).resolve().parent
    backend_data = Path(BACKEND_DIR) / "data.jsonl"
    env_data = os.getenv("DATA_PATH")

    candidates: list[Path] = []
    if env_data:
        env_path = Path(env_data)
        if env_path.is_absolute():
            candidates.append(env_path)
        else:
            candidates.extend(
                [
                    project_root / env_path,
                    Path(BACKEND_DIR) / env_path,
                    Path.cwd() / env_path,
                ]
            )

    candidates.extend([
        backend_data,
        project_root / "backend" / "data.jsonl",
        project_root / "data.jsonl",
    ])

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return str(backend_data)


@st.cache_resource(show_spinner="📦 Loading dataset...")
def load_data() -> pd.DataFrame:
    """Load Reddit posts into a pandas DataFrame via DuckDB."""
    from data.database import get_connection
    from data.loader import load_to_duckdb

    data_path = _resolve_data_path()
    conn = get_connection()

    try:
        count = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    except Exception:
        count = 0

    if count == 0:
        load_to_duckdb(data_path)
        conn = get_connection()

    df = conn.execute("SELECT * FROM posts").df()
    conn.close()
    return df


@st.cache_resource(show_spinner="🔍 Loading search index...")
def load_search_index():
    """Load or build FAISS index and return lightweight lookup artifacts."""
    from ml.embeddings import build_index, load_index

    df = load_data()
    index, id_map = load_index()

    if index is None or id_map is None:
        texts = df["text_combined"].fillna("").tolist()
        post_ids = df["id"].tolist()
        index, id_map, _ = build_index(texts, post_ids)

    id_to_idx = {pid: i for i, pid in enumerate(id_map)}
    return index, id_map, id_to_idx


@st.cache_resource(show_spinner="🧠 Loading embedding matrix...")
def load_embedding_matrix() -> np.ndarray:
    """Load vector matrix only when needed (e.g., clustering page)."""
    index, _, _ = load_search_index()
    if index is None or index.ntotal == 0:
        return np.empty((0, 0), dtype=np.float32)

    vectors = index.reconstruct_n(0, index.ntotal)
    return np.array(vectors, dtype=np.float32)


@st.cache_resource(show_spinner="🕸️ Building network graph...")
def load_network_graph():
    """Build subreddit co-occurrence network."""
    from ml.network import build_subreddit_network

    df = load_data()
    return build_subreddit_network(df)


def filter_df(
    df: pd.DataFrame,
    subreddit: Optional[str] = None,
    start_date=None,
    end_date=None,
) -> pd.DataFrame:
    """Apply subreddit and date filters to the DataFrame."""
    out = df
    if subreddit and subreddit != "All":
        out = out[out["subreddit"] == subreddit]

    if start_date or end_date:
        with_dates = out.assign(
            _date_filter=pd.to_datetime(out["date_only"], errors="coerce").dt.date
        )
        if start_date:
            s = pd.to_datetime(str(start_date), errors="coerce")
            if pd.notnull(s):
                with_dates = with_dates[with_dates["_date_filter"] >= s.date()]
        if end_date:
            e = pd.to_datetime(str(end_date), errors="coerce")
            if pd.notnull(e):
                with_dates = with_dates[with_dates["_date_filter"] <= e.date()]
        out = with_dates.drop(columns=["_date_filter"])

    return out
