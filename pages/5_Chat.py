"""💬 Chat — AI-powered research assistant."""

import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parent.parent)
BACKEND = str(Path(ROOT) / "backend")
for p in [ROOT, BACKEND]:
    if p not in sys.path:
        sys.path.insert(0, p)

import os
import streamlit as st
import pandas as pd
from shared import load_data, load_search_index
from ui import apply_global_styles

st.set_page_config(page_title="Chat | NarrativeScope", page_icon="💬", layout="wide")
apply_global_styles()
st.title("💬 NarrativeScope AI Chat")
st.caption("Ask questions about the Reddit dataset using natural language")

# ── Initialize Chat History ──
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# ── Sidebar ──
with st.sidebar:
    st.header("Chat Settings")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_messages = []
        st.rerun()
    st.divider()
    st.markdown("**How to use:**")
    st.markdown("- Ask about narratives, trends, and patterns")
    st.markdown("- The AI retrieves relevant posts via semantic search")
    st.markdown("- Responses cite specific Reddit posts")
    st.divider()
    has_key = bool(os.getenv("ANTHROPIC_API_KEY"))
    st.markdown(f"🔑 API Key: {'✅ Configured' if has_key else '❌ Missing'}")

# ── Display Chat History ──
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("retrieved_posts"):
            with st.expander(f"📄 {len(msg['retrieved_posts'])} Retrieved Posts"):
                for i, post in enumerate(msg["retrieved_posts"][:5], 1):
                    st.markdown(f"**{i}. [{post.get('subreddit', '')}]** {post.get('title', '')}")
                    st.caption(f"Score: {post.get('score', 0)} | Similarity: {post.get('similarity_score', 0):.2f}")

# ── Chat Input ──
if prompt := st.chat_input("Ask about the Reddit data..."):
    # Show user message
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Searching & analyzing..."):
            try:
                df = load_data()
                index, id_map, _ = load_search_index()

                from ml.embeddings import semantic_search
                search_results = semantic_search(prompt, index, id_map, k=10)
                score_map = {r["post_id"]: r["similarity_score"] for r in search_results}

                retrieved_posts = []
                if score_map:
                    retrieved = df[df["id"].isin(score_map.keys())].copy()
                    retrieved["similarity_score"] = retrieved["id"].map(score_map)
                    retrieved = retrieved.sort_values("similarity_score", ascending=False)

                    for _, row in retrieved.iterrows():
                        retrieved_posts.append({
                            "id": row["id"], "title": row["title"],
                            "subreddit": row["subreddit"], "text": row["text_combined"],
                            "score": int(row["score"] or 0), "author": row["author"],
                            "created_dt": row["created_dt"].isoformat() if pd.notnull(row["created_dt"]) else None,
                            "url": row["url"], "permalink": row["permalink"],
                            "similarity_score": float(row["similarity_score"] or 0.0),
                        })

                # Build conversation history for LLM
                history = []
                for msg in st.session_state.chat_messages[:-1]:
                    if msg["role"] in ("user", "assistant"):
                        history.append({"role": msg["role"], "content": msg["content"]})
                history = history[-6:]

                from llm.chatbot import chat as llm_chat
                response_text = llm_chat(prompt, retrieved_posts, history)

            except Exception as e:
                response_text = (
                    "I ran into a temporary chat issue. Please retry in a moment.\n\n"
                    f"Details: {e}"
                )
                retrieved_posts = []

            st.markdown(response_text)

            if retrieved_posts:
                with st.expander(f"📄 {len(retrieved_posts)} Retrieved Posts"):
                    for i, post in enumerate(retrieved_posts[:5], 1):
                        st.markdown(f"**{i}. [{post.get('subreddit', '')}]** {post.get('title', '')}")
                        st.caption(f"Score: {post.get('score', 0)} | Similarity: {post.get('similarity_score', 0):.2f}")

            st.session_state.chat_messages.append({
                "role": "assistant", "content": response_text,
                "retrieved_posts": retrieved_posts,
            })
