# Google Trends Integration Complete

## Overview

Now using **actual Google Trends data** to enhance trending articles! The system:
1. Fetches trending Football & Cricket articles from RSS feeds (ESPN, BBC)
2. Filters to show only articles from last 1 hour
3. Enhances articles with real Google Trends data (search interest, related queries)

## How It Works

### Step 1: Fetch Trending Articles (RSS)
Every hour, fetch from:
- ESPN Cricket RSS
- BBC Football RSS  
- BBC Cricket RSS
- ESPN Football RSS

Only articles published in the last 60 minutes are saved.

### Step 2: Enhance with Google Trends (NEW!)
Every hour, for each recent article:
- Extract keywords from title
- Query Google Trends for search interest
- Get related trending queries
- Add Google Trends metadata to article

### Result
Each trend article now includes:
```json
{
  "title": "Premier League player rankings",
  "sport": "Football",
  "google_trends": {
    "avg_interest": 134.59,  // Search interest score
    "timeframe": "last 1 hour",
    "keywords_searched": ["players", "Premier"],
    "related_queries": {
      "players": {
        "top": ["nba players", "basketball players"],
        "rising": ["best college football players 2025"]
      }
    }
  }
}
```

## Features

✅ **Real Google Trends Data**
- Search interest scores
- Trending related queries
- Top and rising search terms

✅ **Last 1 Hour Only**
- Articles filtered by publish time
- Fresh content only

✅ **Reliable Sources**
- ESPN Cricket & Football
- BBC Cricket & Football
- Professional sports coverage

✅ **Automatic Enhancement**
- Runs every hour via Celery Beat
- No manual intervention needed

## Schedule

- **Fetch RSS Articles**: Every 1 hour (gets last hour's content)
- **Enhance with Google Trends**: Every 1 hour (adds trends data)
- **Manual Refresh**: Works immediately via frontend or API

## API Endpoints

### Fetch Trends
```bash
POST /api/rss/feeds/fetch-trends/
```
Fetches latest Football & Cricket articles from RSS feeds.

### Enhance with Google Trends
```bash
POST /api/rss/feeds/enhance-trends/
```
Adds Google Trends data to recent articles.

## Installation

pytrends is now installed:
```bash
pip install pytrends==4.9.2
```

## Rate Limiting

- Google Trends API has rate limits (429 errors)
- Added 2-second delay between requests
- Task handles errors gracefully
- Some articles may not get enhanced if rate-limited

## Testing

Test the integration:
```bash
cd backend
source venv/bin/activate
python manage.py shell
```

```python
from rss_fetcher.tasks import fetch_google_trends_sports, enhance_articles_with_google_trends

# Fetch trending articles
result = fetch_google_trends_sports()
print(result)  # {'success': True, 'articles_created': 17}

# Enhance with Google Trends
result = enhance_articles_with_google_trends()
print(result)  # {'success': True, 'articles_enhanced': 17}

# View enhanced article
from cms.models import Article
article = Article.objects.filter(category='trends').first()
if article.trend_data and 'google_trends' in article.trend_data:
    print(article.trend_data['google_trends'])
```

## Current Status

✅ 37 trend articles in database
✅ Google Trends integration working
✅ Enhancement task runs hourly
✅ Manual API endpoints available
✅ Rate limiting handled gracefully

## Data Flow

```
1. RSS Feeds (ESPN/BBC)
   ↓
2. Fetch last 1 hour articles
   ↓
3. Save to database (category='trends')
   ↓
4. Google Trends Enhancement
   ↓
5. Add search interest + related queries
   ↓
6. Display in Trends tab
```

## Next Steps

1. **Restart server** to pick up pytrends installation
2. **Check Trends tab** for enhanced articles
3. **View Google Trends data** in article details
4. **Monitor rate limits** - may need to adjust schedule

## Troubleshooting

If enhancement fails:
- Check if pytrends is installed: `pip list | grep pytrends`
- Check rate limits (429 errors are normal)
- Manual enhancement works via API
- Falls back gracefully if Google Trends unavailable

## Notes

- Google Trends works best with significant keywords (>4 chars)
- Enhancement runs after articles are fetched
- Only recent articles (last hour) get enhanced
- Related queries provide additional trending context
