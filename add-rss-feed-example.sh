#!/bin/bash

# Example script to add an RSS feed via API

# Step 1: Get authentication token
echo "Getting authentication token..."
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])")

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get token. Check your credentials."
  exit 1
fi

echo "✅ Token obtained"

# Step 2: Add RSS Feed
# Replace with your feed details
FEED_NAME="BBC News"
FEED_URL="https://feeds.bbci.co.uk/news/rss.xml"

echo "Adding RSS feed: $FEED_NAME"
curl -X POST http://localhost:8001/api/rss/feeds/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"$FEED_NAME\",
    \"url\": \"$FEED_URL\",
    \"is_active\": true,
    \"fetch_interval\": 60
  }" | python3 -m json.tool

echo ""
echo "✅ Feed added successfully!"

