import html
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from data.database import create_indexes, get_connection, recreate_posts_table


DEFAULT_DATA_PATH = os.getenv("DATA_PATH", str(Path(__file__).resolve().parents[1] / "data.jsonl"))


def _get_value(data: dict[str, Any], key: str, default: Any = None) -> Any:
    value = data.get(key, default)
    return default if value is None else value


def parse_jsonl(data_path: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    with open(data_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                continue

            payload = parsed.get("data", {})
            title = _get_value(payload, "title", "")
            selftext = _get_value(payload, "selftext", "")
            text_combined = html.unescape(f"{title} {selftext}".strip())

            created_utc = float(_get_value(payload, "created_utc", 0.0) or 0.0)
            created_dt = datetime.utcfromtimestamp(created_utc) if created_utc > 0 else None

            score = int(_get_value(payload, "score", 0) or 0)
            num_comments = int(_get_value(payload, "num_comments", 0) or 0)
            num_crossposts = int(_get_value(payload, "num_crossposts", 0) or 0)
            engagement_score = score + (num_comments * 2) + (num_crossposts * 3)

            rows.append(
                {
                    "id": _get_value(payload, "id", ""),
                    "kind": _get_value(parsed, "kind", ""),
                    "title": title,
                    "selftext": selftext,
                    "text_combined": text_combined,
                    "author": _get_value(payload, "author", ""),
                    "author_fullname": _get_value(payload, "author_fullname", ""),
                    "subreddit": _get_value(payload, "subreddit", ""),
                    "subreddit_id": _get_value(payload, "subreddit_id", ""),
                    "subreddit_subscribers": int(_get_value(payload, "subreddit_subscribers", 0) or 0),
                    "score": score,
                    "ups": int(_get_value(payload, "ups", 0) or 0),
                    "upvote_ratio": float(_get_value(payload, "upvote_ratio", 0.0) or 0.0),
                    "num_comments": num_comments,
                    "num_crossposts": num_crossposts,
                    "created_utc": created_utc,
                    "created_dt": created_dt,
                    "date_only": created_dt.date() if created_dt else None,
                    "hour_of_day": created_dt.hour if created_dt else None,
                    "day_of_week": created_dt.strftime("%A") if created_dt else None,
                    "url": _get_value(payload, "url", ""),
                    "permalink": _get_value(payload, "permalink", ""),
                    "domain": _get_value(payload, "domain", ""),
                    "is_self": bool(_get_value(payload, "is_self", False)),
                    "over_18": bool(_get_value(payload, "over_18", False)),
                    "stickied": bool(_get_value(payload, "stickied", False)),
                    "locked": bool(_get_value(payload, "locked", False)),
                    "gilded": int(_get_value(payload, "gilded", 0) or 0),
                    "total_awards_received": int(_get_value(payload, "total_awards_received", 0) or 0),
                    "engagement_score": engagement_score,
                    "is_crosspost": num_crossposts > 0,
                }
            )

    return pd.DataFrame(rows)


def load_to_duckdb(data_path: str = DEFAULT_DATA_PATH) -> dict[str, Any]:
    if not Path(data_path).exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")

    df = parse_jsonl(data_path)
    conn = get_connection()
    recreate_posts_table(conn)

    if not df.empty:
        conn.register("posts_df", df)
        conn.execute("INSERT INTO posts SELECT * FROM posts_df")
        conn.unregister("posts_df")

    create_indexes(conn)

    summary = conn.execute(
        """
        SELECT
            COUNT(*) AS total_posts,
            COUNT(DISTINCT author) AS unique_authors,
            COUNT(DISTINCT subreddit) AS unique_subreddits,
            MIN(created_dt) AS min_created_dt,
            MAX(created_dt) AS max_created_dt
        FROM posts
        """
    ).fetchone()

    result = {
        "total_posts": summary[0] or 0,
        "unique_authors": summary[1] or 0,
        "unique_subreddits": summary[2] or 0,
        "date_range": {
            "start": summary[3].isoformat() if summary[3] else None,
            "end": summary[4].isoformat() if summary[4] else None,
        },
    }

    print("=== NarrativeScope Data Load Summary ===")
    print(f"Total posts: {result['total_posts']}")
    print(f"Unique authors: {result['unique_authors']}")
    print(f"Unique subreddits: {result['unique_subreddits']}")
    print(f"Date range: {result['date_range']['start']} -> {result['date_range']['end']}")

    return result


if __name__ == "__main__":
    load_to_duckdb(DEFAULT_DATA_PATH)
