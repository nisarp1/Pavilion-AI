# Automatic RSS Feed Fetching

## ✅ Overview

The backend is now configured to **automatically fetch newer articles** from RSS feeds on a scheduled basis.

## 🔄 How It Works

1. **Celery Beat** (scheduler) runs the `fetch_rss_feeds` task periodically
2. The task checks all active RSS feeds in the database
3. For each feed, it respects the feed's `fetch_interval` (in minutes)
4. New articles are automatically created with status "fetched"
5. Duplicate articles (by source URL) are skipped

## ⚙️ Configuration

### Fetch Interval

The scheduler runs every **30 minutes by default** (configurable).

To change the interval, set the `RSS_FETCH_INTERVAL_MINUTES` environment variable:

```bash
# In your .env file or environment
RSS_FETCH_INTERVAL_MINUTES=15  # Fetch every 15 minutes
RSS_FETCH_INTERVAL_MINUTES=60  # Fetch every hour
```

### Per-Feed Intervals

Each RSS feed can have its own `fetch_interval` (in minutes). The scheduler respects this:
- If a feed was fetched less than `fetch_interval` minutes ago, it will be skipped
- If it's time to fetch (or never fetched), the feed will be processed

**Default feed interval:** 60 minutes

## 🚀 Setup

### 1. Start Celery Beat

The automatic fetching requires **Celery Beat** to be running. This is already included in the `start-dev.sh` script:

```bash
./start-dev.sh
```

Or manually:

```bash
cd backend
source venv/bin/activate
celery -A pavilion_gemini beat --loglevel=info
```

### 2. Start Celery Worker

You also need a Celery worker to process the tasks:

```bash
cd backend
source venv/bin/activate
celery -A pavilion_gemini worker --loglevel=info
```

### 3. Ensure Redis is Running

Celery requires Redis for message queuing:

```bash
docker-compose up -d redis
```

Or if using Docker Compose:

```bash
docker-compose up -d
```

## 📊 Monitoring

### Check Logs

**Celery Beat logs:**
```bash
tail -f logs/celery-beat.log
```

**Celery Worker logs:**
```bash
tail -f logs/celery-worker.log
```

### Verify Feeds are Active

Make sure your RSS feeds are marked as `is_active=True` in the database. You can:
- Use the admin panel: http://localhost:8000/admin/rss_fetcher/rssfeed/
- Use the API: `GET /api/rss/feeds/`

### Check Last Fetched Time

Each feed tracks `last_fetched_at`. This is updated automatically after each successful fetch.

## 🔍 What Happens During Fetch

1. **Feed Check:** All active feeds are checked
2. **Interval Check:** Feeds that were recently fetched are skipped
3. **RSS Parsing:** Active feeds are fetched and parsed
4. **Duplicate Detection:** Articles are checked by `source_url` to prevent duplicates
5. **Article Creation:** New articles are created with:
   - Status: `fetched`
   - Title, summary, and source URL from RSS
   - Featured image (if available in RSS)
6. **Timestamp Update:** `last_fetched_at` is updated for each processed feed

## 📝 Article Workflow

Fetched articles follow this workflow:

1. **Fetched** → Retrieved from RSS (title, summary, source URL)
2. **Draft** → Generate full content (via "Generate" button or API)
3. **Published** → Article is published and visible

## 🛠️ Manual Testing

You can manually trigger a fetch to test:

**Via Django management command:**
```bash
cd backend
source venv/bin/activate
python manage.py fetch_rss --all
```

**Via API:**
```bash
# Get auth token first
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access')

# Fetch all feeds
curl -X POST http://localhost:8000/api/rss/feeds/fetch_all/ \
  -H "Authorization: Bearer $TOKEN"
```

## ✅ Verification Checklist

- [ ] Redis is running (`docker-compose up -d` or `redis-server`)
- [ ] Celery Worker is running (`celery -A pavilion_gemini worker`)
- [ ] Celery Beat is running (`celery -A pavilion_gemini beat`)
- [ ] At least one RSS feed exists and is active
- [ ] Check logs to see scheduled fetches happening

## 🐛 Troubleshooting

### Feeds Not Fetching Automatically

1. **Check Celery Beat is running:**
   ```bash
   ps aux | grep "celery.*beat"
   ```

2. **Check Celery Beat logs:**
   ```bash
   tail -f logs/celery-beat.log
   ```

3. **Check for errors in worker logs:**
   ```bash
   tail -f logs/celery-worker.log
   ```

4. **Verify Redis connection:**
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

5. **Check feed configuration:**
   - Ensure feeds exist in database
   - Ensure feeds have `is_active=True`
   - Check feed URLs are valid

### Manual Trigger Works But Automatic Doesn't

This usually means Celery Beat is not running. Start it:
```bash
celery -A pavilion_gemini beat --loglevel=info
```

## 📈 Performance Notes

- The scheduler runs every 30 minutes by default
- Only feeds that need fetching (based on interval) are processed
- Up to 10 most recent entries are fetched per feed
- Duplicate detection prevents creating the same article twice

