#!/bin/bash

# Stop development services

echo "Stopping PavilionEnd Development Environment..."
echo ""

# Read PIDs from files
if [ -f "logs/django.pid" ]; then
    DJANGO_PID=$(cat logs/django.pid)
    if ps -p $DJANGO_PID > /dev/null 2>&1; then
        echo "Stopping Django (PID: $DJANGO_PID)..."
        kill $DJANGO_PID
    fi
    rm logs/django.pid
fi

if [ -f "logs/celery.pid" ]; then
    CELERY_PID=$(cat logs/celery.pid)
    if ps -p $CELERY_PID > /dev/null 2>&1; then
        echo "Stopping Celery Worker (PID: $CELERY_PID)..."
        kill $CELERY_PID
    fi
    rm logs/celery.pid
fi

if [ -f "logs/beat.pid" ]; then
    BEAT_PID=$(cat logs/beat.pid)
    if ps -p $BEAT_PID > /dev/null 2>&1; then
        echo "Stopping Celery Beat (PID: $BEAT_PID)..."
        kill $BEAT_PID
    fi
    rm logs/beat.pid
fi

if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "Stopping Frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
    fi
    rm logs/frontend.pid
fi

# Stop Docker services
echo "Stopping Docker services..."
docker-compose down

echo ""
echo "✅ All services stopped!"
echo ""

