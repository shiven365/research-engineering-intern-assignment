from __future__ import annotations

import os
from typing import Any

import anthropic


_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client

SYSTEM_PROMPT = """You are NarrativeScope AI, an intelligence analyst assistant for a social media research platform.
You analyze Reddit posts to help researchers understand how narratives spread across communities.

When given search results (retrieved Reddit posts), you:
1. Answer the user's question based ONLY on the retrieved posts
2. Cite specific posts (by subreddit and title) when making claims
3. Identify narrative patterns and cross-community connections
4. At the end, suggest exactly 2-3 follow-up queries the researcher might explore next

Format your follow-up suggestions as:
FOLLOW-UP QUERIES:
- [query 1]
- [query 2]
- [query 3]

If no relevant posts were found, say so clearly and suggest the user try different search terms."""


def chat(query: str, retrieved_posts: list[dict[str, Any]], conversation_history: list[dict[str, Any]]) -> str:
    if retrieved_posts:
        context = "RETRIEVED POSTS (ranked by semantic relevance):\n\n"
        for i, post in enumerate(retrieved_posts[:8], 1):
            context += f"{i}. [{post['subreddit']}] \"{post['title']}\"\n"
            context += (
                f"   Score: {post['score']} | Author: {post['author']} | "
                f"Similarity: {post.get('similarity_score', 0.0):.2f}\n"
            )
            if post.get("text") and len(post["text"]) > 20:
                context += f"   Content preview: {post['text'][:200]}...\n"
            context += "\n"
    else:
        context = "NO RELEVANT POSTS FOUND for this query.\n"

    user_message = f"{context}\nResearcher question: {query}"
    messages = conversation_history + [{"role": "user", "content": user_message}]

    response = _get_client().messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text
