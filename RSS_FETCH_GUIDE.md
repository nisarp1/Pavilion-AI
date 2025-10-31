# RSS Feed Fetching Guide

## ✅ Current Status

**10 articles** have been successfully fetched from your RSS feed and are now available in the backend!

---

## 📊 View Articles

### Option 1: Via Frontend (Recommended)
1. Open: **http://localhost:3000**
2. Login with: `admin` / `admin123`
3. Navigate to **Articles** page
4. You should see all 10 fetched articles with status "fetched"

### Option 2: Via Backend API
```bash
# Get authentication token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access')

# List all articles
curl http://localhost:8000/api/articles/ \
  -H "Authorization: Bearer $TOKEN"
```

### Option 3: Via Admin Panel
1. Open: **http://localhost:8000/admin/**
2. Login with: `admin` / `admin123`
3. Go to **CMS → Articles**
4. You'll see all fetched articles

---

## 🔄 How to Fetch RSS Feeds

### Method 1: Django Management Command (Easiest)
```bash
cd backend
source venv/bin/activate
export DB_ENGINE=sqlite3

# Fetch all active feeds
python manage.py fetch_rss --all

# Fetch specific feed by ID
python manage.py fetch_rss --feed-id 1
```

### Method 2: Via API Endpoint (Now Works Without Celery)

**Fetch a specific feed:**
```bash
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access')

# Get feed ID first
curl http://localhost:8000/api/rss/feeds/ \
  -H "Authorization: Bearer $TOKEN"

# Fetch specific feed (replace {id} with feed ID)
curl -X POST http://localhost:8000/api/rss/feeds/{id}/fetch/ \
  -H "Authorization: Bearer $TOKEN"

# Fetch ALL feeds
curl -X POST http://localhost:8000/api/rss/feeds/fetch_all/ \
  -H "Authorization: Bearer $TOKEN"
```

### Method 3: Automatic (When Celery is Running)
If you start Celery Beat, RSS feeds will be fetched automatically every hour.

---

## 📝 Article Workflow

1. **Fetched** → Article retrieved from RSS feed (just title, summary, source URL)
2. **Draft** → Click "Generate" to process the article (full content generated)
3. **Published** → Article is published and visible to public

---

## 🔧 What Was Fixed

1. ✅ Created Django management command: `python manage.py fetch_rss`
2. ✅ Updated API endpoints to work synchronously (without Celery)
3. ✅ Successfully fetched 10 articles from your RSS feed
4. ✅ Articles are now visible in backend and frontend

---

## 🚀 Quick Test

To test fetching new articles:
```bash
cd backend
source venv/bin/activate
export DB_ENGINE=sqlite3
python manage.py fetch_rss --all
```

This will fetch new articles from your RSS feed (it won't duplicate existing ones).

---

## 💡 Tips

- Articles are fetched with status **"fetched"** initially
- To generate full content, click the **"Generate"** button in the frontend
- RSS feeds are checked every hour when Celery Beat is running
- You can manually trigger fetches anytime using the methods above

