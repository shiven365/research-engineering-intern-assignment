"""🔗 Network — Subreddit connection explorer."""

import sys
import tempfile
from pathlib import Path

ROOT = str(Path(__file__).resolve().parent.parent)
BACKEND = str(Path(ROOT) / "backend")
for p in [ROOT, BACKEND]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st
import streamlit.components.v1 as components
from shared import load_network_graph
from ml.network import graph_to_json
from ui import apply_global_styles

st.set_page_config(page_title="Network | NarrativeScope", page_icon="🔗", layout="wide")
apply_global_styles()
st.title("🔗 Subreddit Network")
st.caption("Explore how subreddits are connected through shared authors")

# ── Sidebar Controls ──
with st.sidebar:
    st.header("Network Controls")
    min_edge_weight = st.slider("Min Edge Weight", 1, 20, 1)
    centrality_metric = st.selectbox("Centrality Metric", ["pagerank", "betweenness"])
    remove_node = st.text_input("Remove Node (subreddit name)", "")

# ── Build Network ──
with st.spinner("Building network..."):
    graph = load_network_graph()
    graph_data = graph_to_json(graph, remove_node=remove_node if remove_node else None)

    if min_edge_weight > 1:
        graph_data["edges"] = [e for e in graph_data["edges"] if e["weight"] >= min_edge_weight]

if graph_data.get("message"):
    st.info(graph_data["message"])

# ── Stats ──
c1, c2, c3 = st.columns(3)
c1.metric("🔵 Nodes", len(graph_data["nodes"]))
c2.metric("🔗 Edges", len(graph_data["edges"]))
c3.metric("🧩 Components", graph_data.get("components", 0))

st.divider()

# ── Render with Pyvis ──
if graph_data["nodes"]:
    try:
        from pyvis.network import Network as PyvisNetwork

        net = PyvisNetwork(height="550px", width="100%", bgcolor="#0e1117", font_color="#e2e8f0")
        net.barnes_hut(gravity=-30000, central_gravity=0.3, spring_length=100)

        # Size by centrality metric
        centrality_key = centrality_metric
        max_c = max((n.get(centrality_key, 0) for n in graph_data["nodes"]), default=1) or 1

        for node in graph_data["nodes"]:
            size = 10 + (node.get(centrality_key, 0) / max_c) * 40
            community = node.get("community", 0)
            colors = ["#667eea", "#f56565", "#48bb78", "#ed8936", "#9f7aea", "#38b2ac", "#fc8181", "#68d391"]
            color = colors[community % len(colors)]
            title = f"{node['label']}\nPosts: {node['post_count']}\nPageRank: {node['pagerank']:.4f}\nCommunity: {community}"
            net.add_node(node["id"], label=node["label"], size=size, color=color, title=title)

        for edge in graph_data["edges"]:
            net.add_edge(edge["source"], edge["target"], value=edge["weight"],
                         title=f"Weight: {edge['weight']}, Shared Authors: {edge['shared_author_count']}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as f:
            net.save_graph(f.name)
            html_content = open(f.name, "r", encoding="utf-8").read()

        components.html(html_content, height=570, scrolling=False)

    except ImportError:
        st.warning("Pyvis not installed. Install it with: `pip install pyvis`")
        # Fallback: show table
        import pandas as pd
        st.dataframe(pd.DataFrame(graph_data["nodes"]))
else:
    st.info("No network data available with current filters.")

# ── Top Nodes Table ──
st.divider()
st.subheader(f"Top Nodes by {centrality_metric.title()}")
import pandas as pd
nodes_df = pd.DataFrame(graph_data["nodes"])
if not nodes_df.empty:
    display_cols = ["label", "post_count", "avg_score", "pagerank", "betweenness", "community"]
    available = [c for c in display_cols if c in nodes_df.columns]
    st.dataframe(
        nodes_df[available].sort_values(centrality_metric, ascending=False).head(15),
        use_container_width=True, hide_index=True,
    )
