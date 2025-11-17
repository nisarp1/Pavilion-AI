# Quick Start Guide - Pavilion Gemini

## Starting the Development Servers

The application requires two servers to be running:

1. **Backend (Django API)** - Port 8000
2. **Frontend (React/Vite)** - Port 3001

### Option 1: Use the Start Script (Recommended)

```bash
cd /Applications/MAMP/htdocs/pavilion-gemini
./start-dev.sh
```

This will start:
- Django backend on http://localhost:8000
- React frontend on http://localhost:3001
- Celery worker (for background tasks)
- Celery beat (for scheduled tasks)

### Option 2: Manual Start

#### Start Backend (Terminal 1)

```bash
cd /Applications/MAMP/htdocs/pavilion-gemini/backend
source venv/bin/activate
python manage.py runserver
```

Backend will be available at: http://localhost:8000

#### Start Frontend (Terminal 2)

```bash
cd /Applications/MAMP/htdocs/pavilion-gemini/frontend
npm run dev
```

Frontend will be available at: http://localhost:3001

### Verify Services Are Running

1. **Check Backend**: Open http://localhost:8000/api/ in your browser
   - Should see API information JSON

2. **Check Frontend**: Open http://localhost:3001 in your browser
   - Should see the React admin interface

### Troubleshooting

#### Port Already in Use

If you get "port already in use" errors:

```bash
# Kill processes on port 8000
lsof -ti:8000 | xargs kill -9

# Kill processes on port 3001
lsof -ti:3001 | xargs kill -9
```

#### Backend Not Starting

```bash
cd /Applications/MAMP/htdocs/pavilion-gemini/backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### Frontend Not Starting

```bash
cd /Applications/MAMP/htdocs/pavilion-gemini/frontend
rm -rf node_modules
npm install
npm run dev
```

### Stop Services

If you used the start script:

```bash
./stop-dev.sh
```

Or manually kill the processes:

```bash
# Find and kill Django
lsof -ti:8000 | xargs kill -9

# Find and kill Vite
lsof -ti:3001 | xargs kill -9
```

### Access Points

- **Frontend Admin**: http://localhost:3001
- **Backend API**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/

