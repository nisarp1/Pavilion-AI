#!/bin/bash

# Test script to manually trigger RSS fetching

echo "Testing RSS Feed Fetching..."
echo "================================"

# Check if backend is running
if ! curl -s http://localhost:8000/api/auth/login/ > /dev/null 2>&1; then
    echo "Error: Backend server is not running on localhost:8000"
    echo "Please start the backend server first"
    exit 1
fi

echo ""
echo "Note: You need to be logged in to test the fetch endpoints."
echo "You can test manually by:"
echo ""
echo "1. Login at: http://localhost:8000/admin or via the frontend"
echo "2. Get your JWT token"
echo "3. Run:"
echo "   curl -X POST -H 'Authorization: Bearer YOUR_TOKEN' http://localhost:8000/api/rss/feeds/fetch_all/"
echo ""
echo "Or trigger via the frontend refresh button"
echo ""

echo "Test complete!"
