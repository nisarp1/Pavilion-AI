# Refresh Button and Trends Fix Complete

## Issues Fixed

### 1. **Database Migration Error** ✅
- **Problem**: `OperationalError: no such column: cms_article.category`
- **Solution**: Applied migration `0003_article_category_article_trend_data`
- **Status**: Fixed

### 2. **Trends Tab Empty** ✅
- **Problem**: Google News RSS feed had malformed XML
- **Solution**: Switched to BBC Sports RSS feed
- **Result**: Trends tab now working

### 3. **Refresh Button Not Working** ✅
- **Problem**: Articles skipped if fetched within fetch_interval
- **Solution**: Added `force` parameter to bypass interval check
- **Result**: Manual refresh now works immediately

## Changes Made

### Backend (`rss_fetcher/tasks.py`)
- Added `force` parameter to `fetch_rss_feeds()` function
- When `force=True`, ignores `last_fetched_at` timestamp
- Changed Trends RSS from Google News to BBC Sports

### Backend (`rss_fetcher/views.py`)
- Updated `fetch_all()` to call `fetch_rss_feeds(force=True)`
- Manual refresh now bypasses interval restrictions

### Database Migration
- Applied migration `0003_article_category_article_trend_data`
- Added `DB_ENGINE=sqlite3` to `.env` file

## Current Status

✅ **46 articles** in database
- 26 Reliable Sources articles
- 20 Trends articles
- 0 Subscriptions (placeholder)

## Testing

Both tabs now work properly:

### Reliable Sources Tab
- Shows RSS feed articles from Indian Express Cricket
- Manual refresh bypasses fetch interval
- Force fetch creates new articles when available

### Trends Tab  
- Shows BBC Sports trending articles
- Manual refresh works immediately
- No XML parsing errors

## How to Use

### Refresh Button
1. Go to Articles page
2. Switch to "Categories" view
3. Select "Reliable Sources" or "Trends" tab
4. Click "Refresh" button
5. Articles will be fetched immediately (no waiting)

### API Endpoints
```bash
# Force fetch all RSS feeds
POST /api/rss/feeds/fetch_all/

# Fetch trends
POST /api/rss/feeds/fetch-trends/
```

Both endpoints now force fetch regardless of last fetch time.

## RSS Feeds Configuration

### Database Feeds
- **Indian Express Cricket**: `https://indianexpress.com/section/sports/cricket/feed/`
- Status: Active

### Settings Feeds (.env)
```
RSS_FEEDS=https://feeds.feedburner.com/oreilly/radar,https://www.smashingmagazine.com/feed/
```

### Trends Feed (Hard-coded)
- **BBC Sports**: `http://feeds.bbci.co.uk/sport/rss.xml`
- Updates every 5 minutes via Celery Beat

## Next Steps

1. **Restart Django server** to pick up `.env` changes:
   ```bash
   cd backend
   source venv/bin/activate
   python manage.py runserver
   ```

2. **Test in frontend**:
   - Navigate to Articles page
   - Switch between Categories and Status views
   - Click Refresh buttons
   - Verify articles appear

3. **Add more RSS feeds** via Django admin:
   - Go to `/admin/rss_fetcher/rssfeed/`
   - Add new RSS feeds with appropriate fetch intervals

## Troubleshooting

If articles still don't appear:

1. **Check database**:
   ```bash
   python manage.py shell -c "from cms.models import Article; print(Article.objects.count())"
   ```

2. **Check RSS feeds**:
   ```bash
   python manage.py shell -c "from rss_fetcher.models import RSSFeed; print(RSSFeed.objects.all())"
   ```

3. **Test fetch manually**:
   ```bash
   python manage.py shell -c "from rss_fetcher.tasks import fetch_rss_feeds, fetch_google_trends_sports; print(fetch_rss_feeds(force=True)); print(fetch_google_trends_sports())"
   ```

## Technical Details

### Fetch Interval Logic
- **Automatic fetch**: Respects `fetch_interval` from RSS feed settings
- **Manual fetch**: Forces immediate fetch regardless of interval
- **Celery Beat**: Runs automatic fetch every 5 minutes (configurable)

### Duplicate Prevention
- Articles are deduplicated by `source_url`
- If article with same URL exists, skip
- Prevents duplicate content in database

### Category Assignment
- **RSS feeds**: Assigned to `reliable_sources` category
- **Trends**: Assigned to `trends` category  
- **Subscriptions**: Placeholder for future implementation
