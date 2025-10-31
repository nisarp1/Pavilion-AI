# PavilionEnd - Web Application

A scalable CMS platform with RSS feed integration and AI-powered article generation.

## Architecture

- **Frontend**: React SPA with Redux and CKEditor
- **Backend**: Django REST Framework with Microservices architecture
- **Task Queue**: Celery with Redis
- **Database**: PostgreSQL
- **Storage**: AWS S3 (configurable)

## Project Structure

```
pavilion-gemini/
├── backend/           # Django backend services
│   ├── api_gateway/   # Main API entry point
│   ├── cms/           # Article CMS service
│   ├── rss_fetcher/   # RSS feed fetching service
│   └── workers/       # Celery worker tasks
├── frontend/          # React SPA
└── docker-compose.yml # Infrastructure services
```

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker & Docker Compose
- PostgreSQL (via Docker)

### Backend Setup

1. Create virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Start infrastructure services:
```bash
docker-compose up -d
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Start Django development server:
```bash
python manage.py runserver
```

8. Start Celery worker (in separate terminal):
```bash
celery -A pavilion_gemini worker --loglevel=info
```

9. Start Celery beat (for scheduled tasks):
```bash
celery -A pavilion_gemini beat --loglevel=info
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm run dev
```

## Services

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Features

- ✅ Article Management (CRUD)
- ✅ RSS Feed Integration with Scheduled Fetching
- ✅ Asynchronous Article Generation (Celery Workers)
- ✅ Admin/Editor Interface
- ✅ Article Status Workflow (Fetched → Draft → Published)
- ✅ SEO/OG Meta Data Management
- ✅ JWT Authentication
- ✅ Rich Text Editor (CKEditor 5)
- ✅ Responsive UI (Tailwind CSS)

## Quick Start

See [SETUP.md](./SETUP.md) for detailed setup instructions.

**TL;DR:**
```bash
# Start infrastructure
docker-compose up -d

# Setup backend (one-time)
cd backend && bash setup.sh

# Start everything (from project root)
./start-dev.sh
```

## Architecture

### Backend Services

1. **API Gateway** (Django REST Framework)
   - Authentication (JWT)
   - Article CRUD operations
   - API routing

2. **CMS Service** (`cms` app)
   - Article model and management
   - Status workflow
   - SEO metadata

3. **RSS Fetcher Service** (`rss_fetcher` app)
   - Scheduled RSS feed fetching
   - Automatic article creation

4. **Article Generation Workers** (`workers` app)
   - Celery tasks for async processing
   - Content generation and enhancement

### Frontend

- React 18 with Hooks
- Redux Toolkit for state management
- React Router for navigation
- CKEditor 5 for rich text editing
- Tailwind CSS for styling

