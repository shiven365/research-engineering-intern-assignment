import os
from pathlib import Path

import duckdb


DEFAULT_DB_PATH = os.getenv("DB_PATH", str(Path(__file__).resolve().parents[2] / "narrativescope.db"))


def get_connection(db_path: str | None = None) -> duckdb.DuckDBPyConnection:
    """Return a DuckDB connection for the project database."""
    final_path = db_path or DEFAULT_DB_PATH
    return duckdb.connect(final_path)


def init_posts_table(conn: duckdb.DuckDBPyConnection) -> None:
    """Create the posts table if missing."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT,
            kind TEXT,
            title TEXT,
            selftext TEXT,
            text_combined TEXT,
            author TEXT,
            author_fullname TEXT,
            subreddit TEXT,
            subreddit_id TEXT,
            subreddit_subscribers BIGINT,
            score BIGINT,
            ups BIGINT,
            upvote_ratio DOUBLE,
            num_comments BIGINT,
            num_crossposts BIGINT,
            created_utc DOUBLE,
            created_dt TIMESTAMP,
            date_only DATE,
            hour_of_day INTEGER,
            day_of_week TEXT,
            url TEXT,
            permalink TEXT,
            domain TEXT,
            is_self BOOLEAN,
            over_18 BOOLEAN,
            stickied BOOLEAN,
            locked BOOLEAN,
            gilded BIGINT,
            total_awards_received BIGINT,
            engagement_score BIGINT,
            is_crosspost BOOLEAN
        )
        """
    )


def recreate_posts_table(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("DROP TABLE IF EXISTS posts")
    init_posts_table(conn)


def create_indexes(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("CREATE INDEX IF NOT EXISTS idx_posts_subreddit ON posts(subreddit)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_posts_created_utc ON posts(created_utc)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_posts_date_only ON posts(date_only)")
