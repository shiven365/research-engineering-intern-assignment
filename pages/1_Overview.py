"""📊 Overview — Key statistics and top subreddits."""

import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parent.parent)
BACKEND = str(Path(ROOT) / "backend")
for p in [ROOT, BACKEND]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st
import pandas as pd
import plotly.express as px
from shared import load_data
from ui import apply_global_styles

st.set_page_config(page_title="Overview | NarrativeScope", page_icon="📊", layout="wide")
apply_global_styles()
st.title("📊 Overview")
st.caption("Key statistics and insights from the dataset")

df = load_data()
if df is None or df.empty:
    st.warning("No data loaded yet.")
    st.stop()

# ── Metrics ──
c1, c2, c3, c4 = st.columns(4)
c1.metric("📝 Total Posts", f"{len(df):,}")
c2.metric("👤 Unique Authors", f"{df['author'].nunique():,}")
c3.metric("🏘️ Subreddits", f"{df['subreddit'].nunique():,}")

date_min = pd.to_datetime(df["created_dt"]).min()
date_max = pd.to_datetime(df["created_dt"]).max()
c4.metric("📅 Date Range", f"{date_min.strftime('%b %d')} — {date_max.strftime('%b %d, %Y')}")

st.divider()

# ── Top Subreddits + Quick Stats ──
col_chart, col_stats = st.columns([2, 1])

with col_chart:
    st.subheader("Top 10 Subreddits by Post Count")
    top_subs = (
        df.groupby("subreddit").size()
        .sort_values(ascending=False).head(10)
        .reset_index(name="post_count")
    )
    fig = px.bar(
        top_subs, x="post_count", y="subreddit", orientation="h",
        color="post_count", color_continuous_scale="Viridis",
        labels={"post_count": "Posts", "subreddit": ""},
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0", showlegend=False, coloraxis_showscale=False,
        yaxis=dict(autorange="reversed"), margin=dict(l=0, r=0, t=10, b=0), height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

with col_stats:
    st.subheader("Quick Stats")
    st.metric("Average Score", f"{df['score'].mean():.1f}")
    st.metric("Avg Comments", f"{df['num_comments'].mean():.1f}")
    st.metric("Avg Engagement", f"{df['engagement_score'].mean():.1f}")

st.divider()

# ── Activity by Day of Week ──
st.subheader("Post Activity by Day of Week")
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day_counts = df["day_of_week"].value_counts().reindex(day_order).fillna(0)
fig2 = px.bar(
    x=day_order, y=day_counts.values, labels={"x": "Day", "y": "Posts"},
    color=day_counts.values, color_continuous_scale="Plasma",
)
fig2.update_layout(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font_color="#e2e8f0", showlegend=False, coloraxis_showscale=False,
    margin=dict(l=0, r=0, t=10, b=0), height=300,
)
st.plotly_chart(fig2, use_container_width=True)
