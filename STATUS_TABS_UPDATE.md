# Status Tabs Update Complete

## What Was Added

Added **Status-based tabs** to the Articles view, providing users with two different ways to organize their articles:

### 1. **Categories View** (By source type)
- Reliable Sources
- Trends  
- Subscriptions

### 2. **Status View** (By article status) ⭐ NEW
- **Fetched** - Articles freshly fetched from RSS/News feeds
- **Draft** - Articles that have been generated and are ready for editing
- **Published** - Articles that have been published
- **Trash** - Archived/deleted articles

## UI Changes

- Added a **view switcher** with "Categories" and "Status" buttons at the top
- Users can now toggle between the two views
- Each view maintains its own tab state
- Refresh button works for both views

## Why No Articles Show?

The tabs are empty because:

1. **No RSS feeds configured** - You need to add RSS feeds to the database first
2. **No articles fetched yet** - Need to manually trigger fetching via the Refresh button

## How to Get Articles

### Option 1: Via Django Admin UI
1. Go to `/admin`
2. Add RSS feeds in the "Rss feeds" section
3. Click "Refresh" button in the frontend

### Option 2: Via Django Shell
```bash
cd backend
source venv/bin/activate
python manage.py shell
```
```python
from rss_fetcher.models import RSSFeed
from cms.models import Article

# Add a test RSS feed
RSSFeed.objects.create(
    name="ESPN RSS",
    url="http://www.espn.com/espn/rss/news",
    is_active=True,
    fetch_interval=5
)

# Check existing feeds
print(f"Total feeds: {RSSFeed.objects.count()}")
print(f"Total articles: {Article.objects.count()}")
```

### Option 3: Via API
```bash
# After logging in and getting JWT token
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/rss/feeds/fetch_all/

curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/rss/feeds/fetch-trends/
```

### Option 4: Via Frontend
1. Go to Articles page
2. Make sure you're on "Categories" view
3. Click "Refresh" button
4. Wait for articles to appear

## Testing

Once you have articles, you can:

1. **Switch between views**: Click "Categories" or "Status" at the top
2. **Navigate tabs**: Click different tabs in each view
3. **See filtered articles**: Each tab shows only articles matching that category/status
4. **Refresh**: Click the refresh button to manually trigger new fetches
5. **Auto-refresh**: Wait 5 minutes to see automatic updates (Categories view only)

## Status Tab Behaviors

- **Fetched**: Shows new articles from RSS/News feeds
- **Draft**: Shows articles ready for editing/generation
- **Published**: Shows live articles
- **Trash**: Shows archived articles

## Notes

- Status tabs don't have auto-refresh (only Categories do)
- Manual refresh works for all tabs
- Article operations (generate, publish, archive) work in both views
- Empty tabs mean either no articles exist or they're filtered out
