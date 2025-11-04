# Migration Fix Applied

## Issue
You were getting this error:
```
OperationalError: no such column: cms_article.category
```

## Solution
The migration `0003_article_category_article_trend_data.py` was created but not applied to your database.

## What Was Done
1. ✅ Applied migration 0003 to add `category` and `trend_data` fields
2. ✅ Added `DB_ENGINE=sqlite3` to `.env` file

## Next Steps

### Restart the Django Server
The server needs to be restarted to pick up the new database structure:

```bash
cd /Applications/MAMP/htdocs/pavilion-gemini/backend
source venv/bin/activate

# Stop the current server (Ctrl+C in the terminal running it)
# Then restart:
python manage.py runserver
```

### Verify It Works
1. Go to `http://localhost:8000/admin/cms/article/`
2. You should now see the articles page without errors
3. The `category` and `trend_data` fields are now available

### Test the Frontend
1. Go to `http://localhost:3000` (or your frontend URL)
2. Navigate to the Articles page
3. Switch between "Categories" and "Status" views
4. Click "Refresh" to fetch articles

### First Article Fetch
After restarting, you should:
1. Click "Refresh" button in the frontend (Categories view)
2. This will trigger fetching from:
   - RSS feeds configured in settings: https://feeds.feedburner.com/oreilly/radar and https://www.smashingmagazine.com/feed/
   - Google News Sports trends

Or manually via Django shell:
```bash
cd backend
source venv/bin/activate
python manage.py shell
```
```python
from rss_fetcher.tasks import fetch_rss_feeds, fetch_google_trends_sports

# Fetch RSS feeds
result = fetch_rss_feeds()
print(f"RSS feeds: {result}")

# Fetch Google News trends
result = fetch_google_trends_sports()
print(f"Trends: {result}")
```

## Database Info
- **Type**: SQLite
- **Location**: `/Applications/MAMP/htdocs/pavilion-gemini/backend/db.sqlite3`
- **Migrations**: All up to date (0003 applied)

## Troubleshooting

If you still see errors after restarting:

1. **Clear migrations and reapply**:
   ```bash
   cd backend
   source venv/bin/activate
   python manage.py migrate cms zero
   python manage.py migrate cms
   ```

2. **Check database**:
   ```bash
   python manage.py dbshell
   .schema cms_article
   ```

3. **Verify .env file**:
   ```bash
   cat .env | grep DB_ENGINE
   # Should show: DB_ENGINE=sqlite3
   ```

## What Changed in the Database
- Added `category` column (default: 'reliable_sources')
- Added `trend_data` JSON column (for Google News trends data)
