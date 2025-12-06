# Trends Functionality Upgrade

## Overview
We have significantly strengthened the "Trends" fetching capability by integrating **Realtime Google Trends** and **Actual Twitter Trends** (via robust proxy).

## New Features

### 1. Realtime Google Trends
- **Old Behavior**: Relied on Daily Trends RSS.
- **New Behavior**: Now uses `pytrends.realtime_trending_searches(pn='IN')` to get up-to-the-minute trending searches in India.
- **Fallback**: Gracefully falls back to Daily Trends API and then RSS if Realtime fails.

### 2. Actual Twitter Trends (30min & 24h)
- **Source**: Scrapes `trends24.in/india/`, a reliable aggregator of Twitter trends.
- **30-Minute Trends**: Fetches the most recent hourly list (List 0) to capture breaking news.
- **One Day Trends**: Aggregates trends across the last 24 hours to find persistent topics (topics appearing in 3+ hourly lists).
- **Filtering**: Automatically filters for sports-related keywords (Cricket, Football, Players, etc.) to ensure relevant content.

### 3. Enhanced Article Fetching
- The system now processes a combined, deduplicated list of unique topics from:
  1. Google Realtime Trends
  2. Twitter Realtime Trends (30 mins)
  3. Twitter Persistent Trends (24 hours)
- Uses NewsAPI to search and fetch articles for these specific high-value topics.

## Technical Details
- **File Modified**: `backend/rss_fetcher/tasks.py`
- **New Function**: `_get_trends24_sports_trends()` - Handles the scraping and aggregation.
- **Updated Function**: `_get_trending_topics_from_google_trends()` - Added Realtime API support.
- **Updated Function**: `fetch_google_trends_sports()` - Orchestrates the multi-source fetching.

## Verification
- Validated `trends24.in` scraping with a test script (successful).
- Verified `requests` and `BeautifulSoup` are available in the environment.
- Code handles fallbacks and errors gracefully.
