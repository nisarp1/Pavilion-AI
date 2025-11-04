# NewsAPI India Implementation for Sports Trends

## Overview

The system now uses **NewsAPI.org** to fetch hyper-local and hyper-recent sports trends for India. This provides better real-time trending data compared to RSS feeds alone.

## Implementation Details

### How It Works

1. **Primary**: NewsAPI for India sports (last 1 hour, sorted by popularity)
2. **Fallback**: RSS feeds from ESPN/BBC if NewsAPI unavailable
3. **Enhancement**: Google Trends data added to all articles

### NewsAPI Configuration

Add to `.env`:
```bash
NEWS_API_KEY=your_newsapi_key_here
```

Get a free key at: https://newsapi.org/register

### Query Parameters

```python
api_url = 'https://newsapi.org/v2/everything'
params = {
    'q': '(cricket OR football OR ipl OR bcci OR kohli OR dhoni OR messi OR ronaldo OR premier league)',
    'language': 'en',
    'sortBy': 'popularity',  # Most popular/trending first
    'from': '2024-11-02T10:00:00Z',  # Last 1 hour
    'pageSize': 50,
    'apiKey': YOUR_KEY,
}
```

### Features

✅ **Last 1 Hour Filtering** - Only fresh content
✅ **Popularity Sorting** - Trending articles first  
✅ **India Sports Focus** - Cricket, IPL, Football keywords
✅ **Automatic Sport Detection** - Cricket/Football/Sports
✅ **Rich Metadata** - Images, authors, descriptions
✅ **Fallback to RSS** - Graceful degradation

### Sport Detection

Articles automatically categorized:
- **Cricket**: cricket, ipl, bcci, kohli, dhoni, ashes, test match
- **Football**: football, soccer, premier league, messi, ronaldo, world cup, epl
- **Sports**: Generic sports articles

### Data Structure

```json
{
  "title": "Virat Kohli smashes century in IPL",
  "sport": "Cricket",
  "feed_name": "ESPN India",
  "source": "ESPN India",
  "author": "Sports Correspondent",
  "description": "Kohli's amazing innings...",
  "content": "Full article text...",
  "image_url": "https://...",
  "newsapi": true
}
```

## Usage

### Automatic (Celery Beat)

Runs every hour via:
```python
'fetch-trends-sports': {
    'task': 'rss_fetcher.tasks.fetch_google_trends_sports',
    'schedule': timedelta(hours=1),
}
```

### Manual (API)

```bash
POST /api/rss/feeds/fetch-trends/
```

### Manual (Python)

```python
from rss_fetcher.tasks import fetch_google_trends_sports

result = fetch_google_trends_sports()
print(result)
# {'success': True, 'articles_created': 47, 'errors': []}
```

## Advantages

### vs RSS Feeds
- ✅ **Real-time trending** via popularity sorting
- ✅ **Broader coverage** from many sources
- ✅ **Rich metadata** (images, authors, full text)
- ✅ **Better filtering** (time, popularity, keywords)
- ✅ **Country-specific** news

### vs Google Trends
- ✅ **Actual articles** not just search terms
- ✅ **No rate limits** in paid tier
- ✅ **Structured data** ready to use
- ✅ **Reliable API** with support

## Fallback Behavior

```
NewsAPI → (if fails/no results) → RSS Feeds → (always works)
```

This ensures the system always fetches trending articles even if NewsAPI is unavailable.

## Next Steps

1. **Get NewsAPI Key**: Register at https://newsapi.org
2. **Add to .env**: `NEWS_API_KEY=your_key_here`
3. **Restart Server**: Apply configuration
4. **Test**: Manually trigger fetch or wait for auto-run
5. **Monitor**: Check articles in Trends tab

## Cost

- **Free Tier**: 100 requests/day
- **Developer**: $449/month - unlimited
- **Business**: Custom pricing

For hourly fetches (24/day), free tier is sufficient for development/testing.

## Testing

Test without API key (falls back to RSS):
```bash
# RSS feeds still work
python manage.py shell -c "from rss_fetcher.tasks import fetch_google_trends_sports; print(fetch_google_trends_sports())"
```

Test with API key:
```bash
# Add to .env: NEWS_API_KEY=your_key
python manage.py shell -c "from rss_fetcher.tasks import _fetch_newsapi_india_sports; print(_fetch_newsapi_india_sports())"
```

## Expected Results

With NewsAPI configured, you should see:
- 20-50 trending sports articles per hour
- Mix of Cricket (IPL) and Football content
- Real-time popularity scores
- Diverse sources (ESPN India, Times of India, etc.)
- Rich article metadata

## Notes

- NewsAPI "everything" endpoint searches all articles
- "top-headlines" endpoint available but limited to 48 hours
- Free tier has rate limits (100/day)
- Articles deduplicated by URL
- Only English language articles
- Only last 1 hour content saved
