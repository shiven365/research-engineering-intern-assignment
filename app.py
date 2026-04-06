"""NarrativeScope — Narrative Intelligence Platform for Reddit Analysis."""

import streamlit as st
from ui import apply_global_styles

st.set_page_config(
    page_title="NarrativeScope",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_styles()

# ── Sidebar ──
with st.sidebar:
    st.markdown("### 🔍 NarrativeScope")
    st.caption("Narrative Intelligence Platform")
    st.divider()
    st.markdown("Navigate using the pages above ☝️")
    st.divider()
    st.caption("Built with Streamlit • Powered by AI")

# ── Hero Section ──
st.markdown("""
<div class="ns-hero">
    <div class="ns-badge">Narrative Intelligence Dashboard</div>
    <h1>🔍 NarrativeScope</h1>
    <p>Narrative Intelligence Platform for Reddit Analysis</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
NarrativeScope helps researchers understand how **narratives spread across Reddit communities**.
Analyze patterns, discover connections, and gain AI-powered insights from social media data.
""")

# ── Feature Cards ──
features = [
    ("📊", "Overview", "Key stats and top subreddits"),
    ("📈", "Timeline", "Post activity over time"),
    ("🔗", "Network", "Subreddit connections"),
    ("🔮", "Clusters", "Topic clustering with ML"),
    ("💬", "AI Chat", "Ask questions about data"),
]
cards_html = "".join(
    [
        f"""
        <div class="ns-card">
            <div class="ns-card-icon">{icon}</div>
            <h3>{title}</h3>
            <p>{desc}</p>
        </div>
        """
        for icon, title, desc in features
    ]
)
st.markdown(f"<div class=\"ns-feature-grid\">{cards_html}</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption("👈 Select a page from the sidebar to get started")
