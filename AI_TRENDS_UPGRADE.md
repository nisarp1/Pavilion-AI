
# AI-Powered Trends Upgrade

## Problem
Explicit "Sports" filtering by keyword (e.g., "cricket", "football") misses specific entity names that are currently trending but not generically named (e.g., "Shai Hope", "Gunther", "Christchurch", "Ravindra Jadeja"). The user wants the "exact" feel of the X Sports tab.

## Solution: AI Classification
We have replaced the strict keyword filter for Trends24 data with an **AI Classifier (Gemini)**.

### How it works:
1.  **Fetch Raw Candidates**: We scrape the top trends from `trends24.in/india/` (combining the latest hourly list + persistent 24h trends).
2.  **AI Classification**: We send this full raw list (typically ~50-80 items) to Google Gemini Pro 1.5.
3.  **Intelligent Filtering**: The prompt specifically instructs Gemini to:
    *   Identify topics related to Sports (Cricket, WWE, Football, F1, etc.).
    *   Include specific athlete names ("Gunther", "Shai Hope").
    *   Include venues ("Christchurch").
    *   Exclude politics/entertainment.
4.  **Result**: A clean JSON list of sports trends that closely mimics the human-curated X Sports tab.

### Fallback
If the Gemini API fails or returns no results, the system automatically falls back to the previous Keyword Matching method to ensure some data is still returned.

## Status
- **Implemented in**: `backend/rss_fetcher/tasks.py`
- **Function**: `_classify_sports_trends_with_ai`
- **Integration**: Called within `_get_trends24_sports_trends`

This robustly solves the issue of missingtrends like "Gunther" or "Jadeja" without needing to maintain an infinite list of player names.
