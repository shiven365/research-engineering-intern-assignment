"""🔮 Clusters — Topic clustering with ML."""

import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parent.parent)
BACKEND = str(Path(ROOT) / "backend")
for p in [ROOT, BACKEND]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st
import numpy as np
import plotly.express as px
from shared import load_data, load_embedding_matrix, load_search_index
from ui import apply_global_styles

st.set_page_config(page_title="Clusters | NarrativeScope", page_icon="🔮", layout="wide")
apply_global_styles()
st.title("🔮 Topic Clusters")
st.caption("Discover narrative themes using ML-powered clustering")

df = load_data()

# ── Sidebar ──
with st.sidebar:
    st.header("Clustering Controls")
    subreddits = sorted(df["subreddit"].unique().tolist())
    subreddit = st.selectbox("Subreddit", ["All"] + subreddits)
    auto_detect = st.checkbox("Auto-detect clusters", value=True)
    n_clusters = None
    if not auto_detect:
        n_clusters = st.slider("Number of Clusters", 2, 30, 8)

# ── Filter Data ──
filtered = df if subreddit == "All" else df[df["subreddit"] == subreddit]

if filtered.empty:
    st.warning("No data for selected filter.")
    st.stop()

# ── Run Clustering ──
if st.button("🚀 Run Clustering", type="primary", use_container_width=True):
    with st.spinner("Loading embeddings & running clustering..."):
        try:
            index, id_map, id_to_idx = load_search_index()
            embedding_matrix = load_embedding_matrix()
            from ml.clustering import cluster_posts

            post_ids = filtered["id"].tolist()
            selected_idx = [id_to_idx[pid] for pid in post_ids if pid in id_to_idx]

            if not selected_idx:
                st.warning("No embeddings found for selected posts.")
                st.stop()

            texts = filtered["text_combined"].fillna("").tolist()
            emb = embedding_matrix[selected_idx]

            result = cluster_posts(emb, texts, n_clusters=n_clusters)
            st.session_state["cluster_result"] = result
            st.session_state["cluster_titles"] = filtered["title"].tolist()
            st.session_state["cluster_subreddits"] = filtered["subreddit"].tolist()
            st.session_state["cluster_post_ids"] = post_ids

        except Exception as e:
            st.error(f"Clustering failed: {e}")

# ── Display Results ──
if "cluster_result" in st.session_state:
    result = st.session_state["cluster_result"]

    if result.get("warnings"):
        for w in result["warnings"]:
            st.warning(w)

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Clusters Found", result.get("n_clusters_found", 0))
    c2.metric("Total Points", len(result.get("coords", [])))
    c3.metric("Method", "Auto (HDBSCAN)" if n_clusters is None else f"KMeans (k={n_clusters})")

    st.divider()

    # Scatter Plot
    coords = result.get("coords", [])
    labels = result.get("labels", [])
    titles = st.session_state.get("cluster_titles", [])
    subs = st.session_state.get("cluster_subreddits", [])

    if coords:
        import pandas as pd
        plot_df = pd.DataFrame({
            "x": [c[0] for c in coords],
            "y": [c[1] for c in coords],
            "cluster": [str(l) for l in labels],
            "title": titles[:len(coords)] if titles else [""] * len(coords),
            "subreddit": subs[:len(coords)] if subs else [""] * len(coords),
        })

        fig = px.scatter(
            plot_df, x="x", y="y", color="cluster",
            hover_data=["title", "subreddit"],
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={"x": "UMAP-1", "y": "UMAP-2"},
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0", height=500,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        fig.update_traces(marker=dict(size=6, opacity=0.7))
        st.plotly_chart(fig, use_container_width=True)

    # Cluster Topics
    st.divider()
    st.subheader("📋 Cluster Topics")
    topics = result.get("cluster_topics", {})
    for cid, topic in sorted(topics.items(), key=lambda x: int(x[0]) if x[0].lstrip("-").isdigit() else 0):
        label = "🔇 Noise" if cid == "-1" else f"Cluster {cid}"
        st.markdown(f"**{label}**: {topic}")
else:
    st.info("👆 Click **Run Clustering** to analyze topic patterns.")
