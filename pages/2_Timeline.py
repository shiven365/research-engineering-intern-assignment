"""📈 Timeline — Post activity over time."""

import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parent.parent)
BACKEND = str(Path(ROOT) / "backend")
for p in [ROOT, BACKEND]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json
from shared import load_data, filter_df
from ui import apply_global_styles

st.set_page_config(page_title="Timeline | NarrativeScope", page_icon="📈", layout="wide")
apply_global_styles()
st.title("📈 Timeline")
st.caption("Track post activity and narrative trends over time")

df = load_data()

# ── Sidebar Filters ──
with st.sidebar:
    st.header("Filters")
    metric = st.selectbox(
        "Metric", ["post_count", "avg_score", "engagement"],
        format_func=lambda x: {"post_count": "📊 Post Count", "avg_score": "⭐ Avg Score", "engagement": "🔥 Engagement"}[x],
    )
    subreddits = sorted(df["subreddit"].unique().tolist())
    subreddit = st.selectbox("Subreddit", ["All"] + subreddits)
    granularity = st.selectbox(
        "Granularity", ["day", "hour", "week"],
        format_func=lambda x: {"day": "Daily", "hour": "Hourly", "week": "Weekly"}[x],
    )
    date_min = pd.to_datetime(df["created_dt"]).min().date()
    date_max = pd.to_datetime(df["created_dt"]).max().date()
    date_range = st.date_input("Date Range", value=(date_min, date_max), min_value=date_min, max_value=date_max)

# ── Filter ──
sub_filter = subreddit if subreddit != "All" else None
start_d = str(date_range[0]) if isinstance(date_range, (list, tuple)) and len(date_range) == 2 else None
end_d = str(date_range[1]) if isinstance(date_range, (list, tuple)) and len(date_range) == 2 else None
filtered = filter_df(df, sub_filter, start_d, end_d)

if filtered.empty:
    st.warning("No data found for selected filters.")
    st.stop()

# ── Compute Time Series ──
work = filtered.copy()
if granularity == "hour":
    work["bucket"] = pd.to_datetime(work["created_dt"]).dt.floor("h")
elif granularity == "week":
    work["bucket"] = pd.to_datetime(work["created_dt"]).dt.to_period("W").dt.start_time
else:
    work["bucket"] = pd.to_datetime(work["created_dt"]).dt.date

if metric == "avg_score":
    series_df = work.groupby("bucket", as_index=False)["score"].mean().rename(columns={"score": "value"})
elif metric == "engagement":
    series_df = work.groupby("bucket", as_index=False)["engagement_score"].mean().rename(columns={"engagement_score": "value"})
else:
    series_df = work.groupby("bucket", as_index=False).size().rename(columns={"size": "value"})

series_df = series_df.sort_values("bucket")
values = series_df["value"].tolist()

# ── Plot ──
fig = px.line(series_df, x="bucket", y="value", labels={"bucket": "Date", "value": metric.replace("_", " ").title()})
fig.update_traces(line=dict(color="#667eea", width=2), fill="tozeroy", fillcolor="rgba(102,126,234,0.1)")
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0",
    margin=dict(l=0, r=0, t=10, b=0), height=450,
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)"), yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
)
st.plotly_chart(fig, use_container_width=True)

# ── Stats Row ──
trend = "➡️ Stable"
if len(values) > 1:
    slope = values[-1] - values[0]
    trend = "📈 Increasing" if slope > 0 else ("📉 Decreasing" if slope < 0 else "➡️ Stable")

peak_idx = int(np.argmax(values)) if values else 0
c1, c2, c3 = st.columns(3)
c1.metric("Trend", trend)
c2.metric("Peak Value", f"{values[peak_idx]:.1f}" if values else "N/A")
c3.metric("Data Points", str(len(series_df)))

# ── AI Summary ──
st.divider()
st.subheader("🤖 AI Summary")
top_subreddits = work.groupby("subreddit").size().sort_values(ascending=False).head(3).index.tolist()
summary_input = {
    "metric": metric,
    "date_range": {"start": str(series_df["bucket"].iloc[0]) if len(series_df) else None, "end": str(series_df["bucket"].iloc[-1]) if len(series_df) else None},
    "total": int(np.sum(values)) if metric == "post_count" else int(len(filtered)),
    "peak_date": str(series_df["bucket"].iloc[peak_idx]) if len(series_df) else None,
    "peak_value": float(values[peak_idx]) if values else 0.0,
    "trend": trend, "top_subreddits": top_subreddits,
    "avg_value": float(np.mean(values)) if values else 0.0, "data_points": int(len(series_df)),
}
summary_key = json.dumps(summary_input, sort_keys=True, default=str)
summary_cache = st.session_state.setdefault("timeline_ai_summary_cache", {})

if st.button("Generate AI Summary", use_container_width=False):
    if summary_key not in summary_cache:
        try:
            from llm.summarizer import generate_timeseries_summary
            summary_cache[summary_key] = generate_timeseries_summary(summary_input)
        except Exception as e:
            summary_cache[summary_key] = f"AI summary unavailable: {e}"

if summary_key in summary_cache:
    cached_summary = summary_cache[summary_key]
    if cached_summary.startswith("AI summary unavailable:"):
        st.warning(cached_summary)
    else:
        st.info(cached_summary)
else:
    st.caption("Generate on demand to avoid slow backend calls during filtering.")
