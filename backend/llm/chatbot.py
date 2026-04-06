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


def _friendly_llm_error(exc: Exception) -> str:
    message = str(exc)
    lower = message.lower()
    if "credit balance is too low" in lower:
        return "Anthropic credits are currently too low."
    if "authentication" in lower or "invalid api key" in lower or "unauthorized" in lower:
        return "Anthropic authentication failed (check API key)."
    if "timed out" in lower or "connection" in lower or "network" in lower:
        return "Network issue while contacting Anthropic."
    return "LLM request failed."


def _fallback_chat_response(query: str, retrieved_posts: list[dict[str, Any]], reason: str | None = None) -> str:
    if not retrieved_posts:
        message = "I could not find enough relevant posts for that question. Try a more specific query with a subreddit or time period."
        if reason:
            message = f"{message}\n\nNote: {reason}"
        return (
            f"{message}\n\n"
            "FOLLOW-UP QUERIES:\n"
            "- Which subreddits discuss this theme most often?\n"
            "- Show posts with the highest engagement on this topic\n"
            "- Compare this narrative across two communities"
        )

    lines = ["Here is a quick evidence-based summary from the retrieved posts:"]
    for i, post in enumerate(retrieved_posts[:5], 1):
        lines.append(
            f"{i}. [{post.get('subreddit', '')}] \"{post.get('title', '')}\" "
            f"(score {post.get('score', 0)}, similarity {post.get('similarity_score', 0.0):.2f})"
        )

    lines.append("")
    lines.append(
        "Pattern: the discussion appears concentrated in a small set of communities with overlapping framing and repeated high-engagement threads."
    )
    if reason:
        lines.append(f"Note: {reason} Using local summary mode.")

    lines.append("")
    lines.append("FOLLOW-UP QUERIES:")
    lines.append(f"- Which specific claims recur most in posts about '{query}'?")
    lines.append("- Which authors or subreddits act as bridges between clusters?")
    lines.append("- How does engagement change over time for this narrative?")
    return "\n".join(lines)


def chat(query: str, retrieved_posts: list[dict[str, Any]], conversation_history: list[dict[str, Any]]) -> str:
    if not os.getenv("ANTHROPIC_API_KEY"):
        return _fallback_chat_response(query, retrieved_posts, "Missing ANTHROPIC_API_KEY.")

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
    trimmed_history = conversation_history[-6:] if conversation_history else []
    messages = trimmed_history + [{"role": "user", "content": user_message}]

    try:
        response = _get_client().messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=600,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        return response.content[0].text
    except Exception as exc:
        return _fallback_chat_response(query, retrieved_posts, _friendly_llm_error(exc))
