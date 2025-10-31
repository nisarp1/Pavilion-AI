# PavilionEnd - Complete Setup Guide

This guide will help you set up the PavilionEnd CMS web application from scratch.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** (but not Python 3.13 yet - there are compatibility issues with some packages)
- **Node.js 16+** and npm
- **Docker & Docker Compose** (for PostgreSQL and Redis)
- **PostgreSQL client libraries** (optional, for psycopg2-binary if needed)

### Installing PostgreSQL Libraries (if needed)

**macOS:**
```bash
brew install postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install libpq-dev python3-dev
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install postgresql-devel python3-devel
```

## Quick Start

### Option 1: Automated Setup (Recommended)

1. **Start Infrastructure Services:**
```bash
docker-compose up -d
```

2. **Setup Backend:**
```bash
cd backend
bash setup.sh
```

3. **Start Development Environment:**
```bash
# From project root
./start-dev.sh
```

### Option 2: Manual Setup

#### Step 1: Start Infrastructure Services

```bash
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- Redis on port 6379

Wait a few seconds for services to initialize.

#### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Note: If psycopg2-binary installation fails, try:
# pip install psycopg2-binary --no-binary psycopg2-binary
# Or install PostgreSQL libraries first (see Prerequisites)

# Create .env file (copy from .env.example and customize)
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser (for admin access)
python manage.py createsuperuser
```

#### Step 3: Start Backend Services

You'll need **3 terminal windows** for the backend:

**Terminal 1 - Django Server:**
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
cd backend
source venv/bin/activate
celery -A pavilion_gemini worker --loglevel=info
```

**Terminal 3 - Celery Beat (Scheduler):**
```bash
cd backend
source venv/bin/activate
celery -A pavilion_gemini beat --loglevel=info
```

#### Step 4: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/api/

## Environment Variables

Key environment variables in `backend/.env`:

- `SECRET_KEY`: Django secret key (generate one)
- `DEBUG`: Set to `True` for development
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: PostgreSQL credentials
- `REDIS_URL`: Redis connection URL
- `CORS_ALLOWED_ORIGINS`: Allowed frontend origins
- `RSS_FEEDS`: Comma-separated RSS feed URLs

## Troubleshooting

### psycopg2-binary Installation Issues

If you encounter issues installing `psycopg2-binary`:

1. Install PostgreSQL development libraries (see Prerequisites)
2. Try: `pip install psycopg2-binary --no-binary psycopg2-binary`
3. Or use SQLite for development (modify `settings.py` DATABASES)

### Database Connection Issues

- Ensure Docker containers are running: `docker-compose ps`
- Check PostgreSQL logs: `docker-compose logs postgres`
- Verify database credentials in `.env`

### Celery Not Working

- Ensure Redis is running: `docker-compose ps`
- Check Redis connection: `redis-cli ping`
- Verify `REDIS_URL` in `.env`

### Frontend Not Connecting to Backend

- Ensure backend is running on port 8000
- Check CORS settings in `backend/pavilion_gemini/settings.py`
- Verify `CORS_ALLOWED_ORIGINS` in `.env`

## Project Structure

```
pavilion-gemini/
├── backend/              # Django backend
│   ├── cms/              # CMS app (articles)
│   ├── rss_fetcher/      # RSS feed fetcher
│   ├── workers/          # Celery tasks
│   ├── pavilion_gemini/  # Project settings
│   └── manage.py
├── frontend/             # React frontend
│   └── src/
│       ├── components/   # React components
│       ├── store/        # Redux store
│       └── services/     # API services
├── docker-compose.yml    # Infrastructure services
└── README.md
```

## Next Steps

1. **Configure RSS Feeds**: Add RSS feed URLs in `.env` or via admin panel
2. **Create Articles**: Use the admin panel or API to create articles
3. **Generate Articles**: Click "Generate" on fetched articles to process them
4. **Edit & Publish**: Use the frontend interface to edit and publish articles

## Production Deployment

For production:

1. Set `DEBUG=False` in `.env`
2. Generate secure `SECRET_KEY`
3. Configure proper database (use managed PostgreSQL)
4. Set up proper Redis instance
5. Configure AWS S3 for media storage
6. Use a proper WSGI server (Gunicorn, uWSGI)
7. Set up reverse proxy (Nginx)
8. Configure SSL/TLS certificates

## Support

For issues or questions, please refer to the main README.md file.

