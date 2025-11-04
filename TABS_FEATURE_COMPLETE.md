# Three Tabs Feature Implementation Complete

## Overview
Successfully implemented three tabs for fetched articles in the Pavilion Gemini application with automatic refresh capabilities and manual refresh buttons.

## Features Implemented

### 1. **Two Tab Views**
Users can switch between two different tab views:

#### **Categories View** (Original tabs by source type)
- **Reliable Sources**: Displays articles from RSS feeds configured in the backend
- **Trends**: Displays trending sports articles from Google News
- **Subscriptions**: Placeholder for future user subscriptions

#### **Status View** (New tabs by article status)
- **Fetched**: Articles freshly fetched from RSS/News feeds
- **Draft**: Articles that have been generated and are ready for editing
- **Published**: Articles that have been published
- **Trash**: Archived/deleted articles

### 2. **Automatic Refresh (5-minute interval)**
- Reliable Sources tab: Auto-fetches RSS feeds every 5 minutes
- Trends tab: Auto-fetches Google News Sports trending topics every 5 minutes
- Only applies to Categories view tabs

### 3. **Manual Refresh Button**
- Added refresh button in the UI for each view
- Shows loading spinner during refresh
- Handles errors gracefully with user feedback
- Fetches new articles and refreshes the current view

## Backend Changes

### Models (`cms/models.py`)
- Added `category` field to Article model with choices:
  - `reliable_sources`
  - `trends`
  - `subscriptions`
- Added `trend_data` JSON field for storing Google News trending data

### Serializers (`cms/serializers.py`)
- Updated `ArticleSerializer` and `ArticleListSerializer` to include `category` and `trend_data` fields

### Views (`cms/views.py`)
- Added `category` filter support in `ArticleViewSet.get_queryset()`

### Tasks (`rss_fetcher/tasks.py`)
- Updated `fetch_single_rss_feed()` to accept `category` and `trend_data` parameters
- Created `fetch_google_trends_sports()` task to fetch Google News Sports RSS feed
- Updated RSS feed fetching to default to 'reliable_sources' category

### Views (`rss_fetcher/views.py`)
- Added `fetch_trends()` action endpoint at `/api/rss/feeds/fetch-trends/`
- Supports both Celery async and synchronous execution

### Settings (`pavilion_gemini/settings.py`)
- Added `fetch-google-trends` task to Celery Beat schedule
- Runs every 5 minutes (configurable via `RSS_FETCH_INTERVAL_MINUTES`)

### Database Migration
- Created migration `0003_article_category_article_trend_data.py`
- Adds `category` and `trend_data` fields to Article model

## Frontend Changes

### Redux Slice (`store/slices/articleSlice.js`)
- Updated `fetchArticles` to accept `category` parameter
- Added `fetchTrends` thunk to manually fetch trends
- Added `fetchAllFeeds` thunk to manually fetch all RSS feeds

### Article List Component (`components/Articles/ArticleList.jsx`)
- Implemented dual tab system with view switcher (Categories vs Status)
- Categories view: Reliable Sources, Trends, Subscriptions
- Status view: Fetched, Draft, Published, Trash
- Added auto-refresh functionality (5-minute interval for Reliable Sources and Trends)
- Added manual refresh button with loading state
- Updated all article operations to work with active tab/view
- Improved UI with tab styling and active state indication

## API Endpoints

### GET `/api/articles/`
- Query parameters: `category` (reliable_sources, trends, subscriptions), `status` (optional)
- Returns filtered articles based on category and status

### POST `/api/rss/feeds/fetch_all/`
- Manually triggers fetching of all active RSS feeds
- Returns count of articles created

### POST `/api/rss/feeds/fetch-trends/`
- Manually triggers fetching of Google News Sports trending topics
- Returns count of articles created

## Google News RSS Feed

Due to Google Trends not having a public RSS feed, we're using Google News Sports RSS feed instead:
- URL: `https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1WlhRZ0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en`
- Category: Sports
- Updates: Every 5 minutes via Celery Beat

## Initial Setup

**Important**: To see articles in "Reliable Sources" and "Trends" tabs, you need to:

1. **Add RSS feeds** to the database via Django admin or API:
   ```bash
   # Using Django shell
   python manage.py shell
   ```
   ```python
   from rss_fetcher.models import RSSFeed
   
   # Add RSS feed
   RSSFeed.objects.create(
       name="ESPN RSS",
       url="http://www.espn.com/espn/rss/news",
       is_active=True,
       fetch_interval=5
   )
   ```

2. **Manually trigger fetching** via:
   - Frontend: Click the "Refresh" button on Categories view
   - API: `POST /api/rss/feeds/fetch_all/` and `POST /api/rss/feeds/fetch-trends/`
   - Command line: `python manage.py fetch_rss --all`

3. **Wait for automatic fetch**: Celery Beat will fetch every 5 minutes if configured

## Testing

### To test the implementation:

1. **Run migrations**:
   ```bash
   cd backend
   source venv/bin/activate
   python manage.py migrate
   ```

2. **Start backend**:
   ```bash
   python manage.py runserver
   ```

3. **Start frontend**:
   ```bash
   cd ../frontend
   npm run dev
   ```

4. **Test tabs**:
   - Navigate to Articles page
   - Switch between Reliable Sources, Trends, and Subscriptions tabs
   - Click Refresh button to manually trigger fetch
   - Wait 5 minutes to see auto-refresh

5. **Test API endpoints**:
   ```bash
   # Fetch articles by category
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        "http://localhost:8000/api/articles/?category=trends"
   
   # Manual refresh trends
   curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
        http://localhost:8000/api/rss/feeds/fetch-trends/
   ```

## Notes

- The Subscriptions tab is a placeholder for future implementation
- All three tabs share the same article management features (generate, publish, archive)
- Auto-refresh is controlled by Celery Beat schedule
- Manual refresh works synchronously if Celery is not available
- Google News RSS feed provides trending sports articles instead of Google Trends

## Future Enhancements

- Implement Subscriptions category functionality
- Add more Google News categories
- Add tab-specific settings for refresh intervals
- Add notification system for new articles
- Implement article deduplication across tabs
