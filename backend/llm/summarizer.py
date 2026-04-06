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


def generate_timeseries_summary(series_data: dict[str, Any]) -> str:
    prompt = f"""You are a data analyst for a social media research platform studying narrative spread on Reddit.

Here is a time-series summary of Reddit post activity:
- Metric: {series_data['metric']}
- Date range: {series_data['date_range']['start']} to {series_data['date_range']['end']}
- Total posts in period: {series_data['total']}
- Peak activity: {series_data['peak_value']} posts on {series_data['peak_date']}
- Overall trend: {series_data['trend']}
- Most active communities: {', '.join(series_data['top_subreddits'])}
- Daily average: {series_data['avg_value']:.1f} posts

Write exactly 2-3 sentences for a non-technical audience explaining:
1. What the trend shows
2. When/why there may have been a spike
3. What this might mean for narrative spread

Be specific with numbers. Do not use jargon. Do not mention "time series" or "data points"."""

    message = _get_client().messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
