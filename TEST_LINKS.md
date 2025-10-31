# PavilionEnd - Test Links & Credentials

## ✅ Setup Complete!

Both backend and frontend are now running.

---

## 🔗 Backend API Test Links

### Base URL
**http://localhost:8000**

### Admin Panel
**http://localhost:8000/admin/**
- **Username:** `admin`
- **Password:** `admin123`

### API Endpoints

#### Authentication
- **Login:** `POST http://localhost:8000/api/auth/login/`
  ```json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```
- **Refresh Token:** `POST http://localhost:8000/api/auth/refresh/`
- **Verify Token:** `POST http://localhost:8000/api/auth/verify/`

#### Articles API (Requires Authentication)
- **List Articles:** `GET http://localhost:8000/api/articles/`
- **Get Article:** `GET http://localhost:8000/api/articles/{id}/`
- **Create Article:** `POST http://localhost:8000/api/articles/`
- **Update Article:** `PATCH http://localhost:8000/api/articles/{id}/`
- **Generate Article:** `POST http://localhost:8000/api/articles/{id}/generate/`
- **Publish Article:** `POST http://localhost:8000/api/articles/{id}/publish/`
- **Archive Article:** `POST http://localhost:8000/api/articles/{id}/archive/`

#### RSS Feeds API (Requires Authentication)
- **List Feeds:** `GET http://localhost:8000/api/rss/feeds/`
- **Create Feed:** `POST http://localhost:8000/api/rss/feeds/`
- **Fetch Feed:** `POST http://localhost:8000/api/rss/feeds/{id}/fetch/`

---

## 🎨 Frontend

### Application URL
**http://localhost:3000**

### Login Credentials
- **Username:** `admin`
- **Password:** `admin123`

---

## 🧪 Quick API Tests

### Test 1: Get Authentication Token

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Response:
```json
{
  "refresh": "...",
  "access": "..."
}
```

### Test 2: List Articles (with token)

```bash
curl http://localhost:8000/api/articles/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test 3: Create Article

```bash
curl -X POST http://localhost:8000/api/articles/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Article",
    "summary": "This is a test article",
    "body": "<p>Article content here</p>",
    "status": "draft"
  }'
```

---

## 📝 Next Steps

1. **Test Backend API:** Use the links above or Postman/Thunder Client
2. **Access Frontend:** Open http://localhost:3000 and login
3. **Configure Gemini API:** Once you provide the API key, we'll integrate it for content generation

---

## 🔧 Integration with Gemini AI

Once you provide the Gemini API details, we'll update the article generation worker to use Gemini for:
- Enhanced content creation
- Article body generation
- SEO optimization
- Content summarization

---

## 📊 Current Status

- ✅ Backend running on port 8000
- ✅ Frontend running on port 3000
- ✅ Database initialized (SQLite)
- ✅ Admin user created
- ✅ API endpoints configured
- ⏳ Waiting for Gemini API configuration

---

## 🐛 Troubleshooting

If services stop, restart them:

**Backend:**
```bash
cd backend
source venv/bin/activate
export DB_ENGINE=sqlite3
python manage.py runserver 0.0.0.0:8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

