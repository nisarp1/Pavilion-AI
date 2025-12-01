# Cloudways Quick Start Guide

This is a condensed version of the deployment guide for quick reference.

## Architecture Overview

```
dev.pavilionend.in/
├── /                    → WordPress (pavilion-theme)
├── /admin               → React Frontend (pavilion-gemini frontend)
└── /super-admin         → Django Backend (pavilion-gemini backend)
    ├── /api             → Django REST API
    ├── /admin           → Django Admin Panel
    ├── /media           → Media files
    └── /static          → Static files
```

## Quick Setup Steps

### 1. Create Applications in Cloudways

Create 3 applications:
1. **WordPress** → `dev.pavilionend.in`
2. **Python/Django** → `dev.pavilionend.in/super-admin`
3. **Static/Node.js** → `dev.pavilionend.in/admin`

### 2. Deploy WordPress

```bash
# Upload theme to WordPress themes directory
cd /home/master/applications/[WORDPRESS_APP_ID]/public_html/wp-content/themes/
# Upload pavilion-theme here
```

Activate theme in WordPress admin.

### 3. Deploy Django Backend

```bash
# Clone repository
cd /home/master/applications/[DJANGO_APP_ID]/public_html/
git clone [repo-url] .

# Setup virtual environment
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Create .env file (see CLOUDWAYS_ENV_TEMPLATE.txt)
nano .env

# Setup database and run migrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic

# Start services (see full guide for systemd setup)
```

### 4. Deploy React Frontend

```bash
# Clone repository
cd /home/master/applications/[FRONTEND_APP_ID]/public_html/
git clone [repo-url] temp
mv temp/frontend/* .
rm -rf temp

# Create .env.production
echo "VITE_API_BASE_URL=/super-admin/api/" > .env.production

# Update vite.config.js to add base: '/admin/'
# Update main.jsx to add basename="/admin" to BrowserRouter

# Build
npm install
npm run build
```

### 5. Configure Nginx

Use the configuration from `CLOUDWAYS_NGINX_CONFIG.conf`:
- Replace `[APP_ID]` placeholders
- Replace `[PHP_VERSION]`
- Test: `sudo nginx -t`
- Reload: `sudo systemctl reload nginx`

### 6. Install SSL

Via Cloudways panel:
- SSL Certificate → Let's Encrypt SSL
- Enter domain: `dev.pavilionend.in`
- Install and enable Force HTTPS

## Critical Configuration Files

### Django Settings Update

Add to `backend/pavilion_gemini/settings.py`:

```python
# Add subdirectory middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'pavilion_gemini.subdirectory_middleware.SubdirectoryMiddleware',  # ADD THIS
    'corsheaders.middleware.CorsMiddleware',
    # ... rest
]
```

### React main.jsx Update

```javascript
<BrowserRouter basename="/admin">
  <App />
</BrowserRouter>
```

### React vite.config.js Update

```javascript
export default defineConfig({
  plugins: [react()],
  base: '/admin/',
  // ... rest
})
```

## Essential Commands

```bash
# Django
cd backend && source venv/bin/activate
python manage.py migrate
python manage.py collectstatic

# Services
sudo systemctl restart pavilion-gunicorn
sudo systemctl restart pavilion-celery
sudo systemctl restart pavilion-celery-beat

# Nginx
sudo nginx -t
sudo systemctl reload nginx

# React
npm run build

# Logs
tail -f /home/master/applications/[APP_ID]/logs/error.log
```

## Quick Troubleshooting

**502 Bad Gateway**
- Check Gunicorn: `sudo systemctl status pavilion-gunicorn`
- Check port: `netstat -tlnp | grep 8000`

**Blank React Page**
- Check build: `ls -la dist/`
- Check browser console
- Verify base path in vite.config.js

**Django URLs Not Working**
- Verify middleware added
- Check Nginx proxy headers
- Test direct: `curl http://127.0.0.1:8000/api/`

**CORS Errors**
- Update CORS_ALLOWED_ORIGINS in .env
- Restart Gunicorn

## File Locations Reference

```
WordPress:
/home/master/applications/[WORDPRESS_APP_ID]/public_html/

Django:
/home/master/applications/[DJANGO_APP_ID]/public_html/backend/
.env → /home/master/applications/[DJANGO_APP_ID]/public_html/backend/.env

React:
/home/master/applications/[FRONTEND_APP_ID]/public_html/
dist/ → Build output
.env.production → Environment variables

Nginx Config:
/etc/nginx/sites-available/ (or via Cloudways panel)
```

## Environment Variables Quick Reference

**Django (.env)**
- `SECRET_KEY` - Generate with `openssl rand -hex 32`
- `DEBUG=False`
- `ALLOWED_HOSTS=dev.pavilionend.in,www.dev.pavilionend.in`
- `CORS_ALLOWED_ORIGINS=https://dev.pavilionend.in,https://www.dev.pavilionend.in`
- Database credentials
- `REDIS_URL=redis://localhost:6379/0`
- API keys (Gemini, News API, etc.)

**React (.env.production)**
- `VITE_API_BASE_URL=/super-admin/api/`

## Testing URLs

- WordPress: `https://dev.pavilionend.in`
- React Frontend: `https://dev.pavilionend.in/admin`
- Django API: `https://dev.pavilionend.in/super-admin/api/`
- Django Admin: `https://dev.pavilionend.in/super-admin/admin/`

---

For detailed instructions, see `CLOUDWAYS_DEPLOYMENT_GUIDE.md`

