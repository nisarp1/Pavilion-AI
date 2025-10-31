#!/bin/bash

# Development startup script for PavilionEnd

echo "Starting PavilionEnd Development Environment..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start infrastructure services
echo "📦 Starting infrastructure services (PostgreSQL, Redis)..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check backend setup
if [ ! -d "backend/venv" ]; then
    echo "⚠️  Backend virtual environment not found. Running setup..."
    cd backend
    bash setup.sh
    cd ..
else
    echo "✅ Backend environment ready"
fi

# Start backend in background
echo ""
echo "🚀 Starting backend services..."
echo "   - Django API Server"
echo "   - Celery Worker"
echo "   - Celery Beat"
echo ""

cd backend
source venv/bin/activate

# Start Django (background)
python manage.py runserver > ../logs/django.log 2>&1 &
DJANGO_PID=$!

# Start Celery Worker (background)
celery -A pavilion_gemini worker --loglevel=info > ../logs/celery-worker.log 2>&1 &
CELERY_PID=$!

# Start Celery Beat (background)
celery -A pavilion_gemini beat --loglevel=info > ../logs/celery-beat.log 2>&1 &
BEAT_PID=$!

cd ..

# Create logs directory if it doesn't exist
mkdir -p logs

# Save PIDs
echo $DJANGO_PID > logs/django.pid
echo $CELERY_PID > logs/celery.pid
echo $BEAT_PID > logs/beat.pid

echo "✅ Backend services started!"
echo "   - Django: http://localhost:8000 (PID: $DJANGO_PID)"
echo "   - Celery Worker: Running (PID: $CELERY_PID)"
echo "   - Celery Beat: Running (PID: $BEAT_PID)"
echo ""

# Check frontend setup
if [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  Frontend dependencies not installed. Installing..."
    cd frontend
    npm install
    cd ..
else
    echo "✅ Frontend dependencies ready"
fi

# Start frontend
echo "🚀 Starting frontend..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo $FRONTEND_PID > logs/frontend.pid

echo "✅ Frontend started: http://localhost:3000 (PID: $FRONTEND_PID)"
echo ""
echo "=========================================="
echo "✨ PavilionEnd is running!"
echo "=========================================="
echo ""
echo "Services:"
echo "  - Frontend:    http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - Admin:       http://localhost:8000/admin"
echo ""
echo "Logs are in the ./logs directory"
echo ""
echo "To stop all services, run: ./stop-dev.sh"
echo ""

