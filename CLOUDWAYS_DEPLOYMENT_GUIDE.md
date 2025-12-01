# Cloudways Deployment Guide for Pavilion Projects

This guide covers deploying both `pavilion-theme` (WordPress) and `pavilion-gemini` (Django + React) to Cloudways under the domain `dev.pavilionend.in`.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Cloudways Server Setup](#cloudways-server-setup)
3. [WordPress Installation & Theme Deployment](#wordpress-installation--theme-deployment)
4. [Django Backend Deployment](#django-backend-deployment)
5. [React Frontend Deployment](#react-frontend-deployment)
6. [Nginx Configuration](#nginx-configuration)
7. [Environment Variables](#environment-variables)
8. [Database Setup](#database-setup)
9. [SSL Certificate Setup](#ssl-certificate-setup)
10. [Post-Deployment Checklist](#post-deployment-checklist)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Cloudways account with server created
- Domain `dev.pavilionend.in` DNS already pointed to Cloudways server IP
- SSH access to Cloudways server
- Git repository access
- All API keys and credentials ready (Gemini, Google Cloud, News API, etc.)

---

## Cloudways Server Setup

### 1. Create Applications in Cloudways

You'll need to create **3 separate applications** on your Cloudways server:

#### Application 1: WordPress (Main Site)
- **Application Name**: `pavilion-wordpress`
- **Application URL**: `dev.pavilionend.in`
- **PHP Version**: 8.1 or 8.2
- **Project Name**: Create a new project or use existing

#### Application 2: Django Backend (Python)
- **Application Name**: `pavilion-gemini-backend`
- **Application URL**: `dev.pavilionend.in/super-admin` (will be configured via Nginx)
- **Python Version**: 3.11 or 3.12
- **Project Name**: Same as above

#### Application 3: React Frontend (Static Site)
- **Application Name**: `pavilion-gemini-frontend`
- **Application URL**: `dev.pavilionend.in/admin` (will be configured via Nginx)
- **Application Type**: Static Site or use Node.js app
- **Project Name**: Same as above

### 2. Server Requirements

Ensure your Cloudways server has:
- **PHP**: 8.1+ (for WordPress)
- **Python**: 3.11+ (for Django)
- **Node.js**: 18+ (for building React app)
- **PostgreSQL**: 13+ (for Django database)
- **Redis**: Latest (for Celery)
- **Nginx**: Latest (managed by Cloudways)

### 3. Access Server via SSH

1. Go to Cloudways Platform → Your Server → **Master Credentials**
2. Note down SSH credentials
3. Connect via SSH:
```bash
ssh username@your-server-ip
```

---

## WordPress Installation & Theme Deployment

### 1. Install WordPress

1. In Cloudways, go to your WordPress application
2. Click **"Install Now"** if not already installed
3. Complete WordPress installation wizard
4. Note down admin credentials

### 2. Upload Pavilion Theme

#### Option A: Via SFTP/SSH
```bash
# Navigate to WordPress themes directory
cd /home/master/applications/[APP_ID]/public_html/wp-content/themes/

# Clone or upload pavilion-theme
# If using Git:
git clone [your-repo-url]/pavilion-theme.git pavilion

# Or upload via SFTP to this directory
```

#### Option B: Via WordPress Admin
1. Go to WordPress Admin → Appearance → Themes
2. Upload `pavilion-theme` as ZIP file
3. Activate the theme

### 3. Configure WordPress

1. **Set Permalink Structure**:
   - Go to Settings → Permalinks
   - Select "Post name" or custom structure
   - Save changes

2. **Update Site URL**:
   - Go to Settings → General
   - WordPress Address (URL): `https://dev.pavilionend.in`
   - Site Address (URL): `https://dev.pavilionend.in`
   - Save changes

3. **Activate Theme**:
   - Go to Appearance → Themes
   - Activate "Pavilion" theme

### 4. Configure Theme Settings

Update `functions.php` or theme settings to point API to:
- API Base URL: `https://dev.pavilionend.in/super-admin/api/`

---

## Django Backend Deployment

### 1. Prepare Django Application Directory

```bash
# SSH into server
ssh username@your-server-ip

# Navigate to your Django application directory
cd /home/master/applications/[DJANGO_APP_ID]/public_html/

# Clone repository
git clone [your-repo-url]/pavilion-gemini.git .

# Or create directory structure manually
mkdir -p backend
cd backend
```

### 2. Set Up Python Virtual Environment

```bash
cd /home/master/applications/[DJANGO_APP_ID]/public_html/backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install additional system dependencies if needed
pip install gunicorn
```

### 3. Configure Environment Variables

Create `.env` file in `/home/master/applications/[DJANGO_APP_ID]/public_html/backend/`:

```bash
cd /home/master/applications/[DJANGO_APP_ID]/public_html/backend
nano .env
```

Add the following configuration:

```env
# Django Settings
SECRET_KEY=your-super-secret-key-here-generate-with-openssl-rand-hex-32
DEBUG=False
ALLOWED_HOSTS=dev.pavilionend.in,www.dev.pavilionend.in

# Database (Cloudways PostgreSQL)
DB_ENGINE=postgresql
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# CORS Settings
CORS_ALLOWED_ORIGINS=https://dev.pavilionend.in,https://www.dev.pavilionend.in

# Redis (Cloudways Redis)
REDIS_URL=redis://localhost:6379/0

# Celery Settings
RSS_FETCH_INTERVAL_MINUTES=5

# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key

# Google Cloud Text-to-Speech
GOOGLE_APPLICATION_CREDENTIALS=/home/master/applications/[DJANGO_APP_ID]/public_html/backend/credentials/google-tts-key.json

# News API
NEWS_API_KEY=your-news-api-key

# AWS S3 (Optional - for media storage)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# RSS Feeds (comma-separated)
RSS_FEEDS=https://example.com/feed1,https://example.com/feed2
```

**Important**: 
- Generate SECRET_KEY: `openssl rand -hex 32`
- Upload `google-tts-key.json` to `backend/credentials/` directory
- Set proper file permissions: `chmod 600 backend/credentials/google-tts-key.json`

### 4. Set Up PostgreSQL Database

1. **Via Cloudways Panel**:
   - Go to your server → Database Management
   - Create new database: `pavilion_gemini`
   - Create database user with password
   - Note down credentials

2. **Via SSH**:
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE pavilion_gemini;
CREATE USER pavilion_user WITH PASSWORD 'your_secure_password';
ALTER ROLE pavilion_user SET client_encoding TO 'utf8';
ALTER ROLE pavilion_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pavilion_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE pavilion_gemini TO pavilion_user;
\q
```

### 5. Run Django Migrations

```bash
cd /home/master/applications/[DJANGO_APP_ID]/public_html/backend
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### 6. Set Up Redis

Redis should be available via Cloudways. Verify connection:
```bash
redis-cli ping
# Should return: PONG
```

### 7. Set Up Celery Workers

Create systemd service files for Celery:

```bash
sudo nano /etc/systemd/system/pavilion-celery.service
```

Add:
```ini
[Unit]
Description=Pavilion Celery Worker
After=network.target

[Service]
Type=forking
User=master
Group=master
WorkingDirectory=/home/master/applications/[DJANGO_APP_ID]/public_html/backend
Environment="PATH=/home/master/applications/[DJANGO_APP_ID]/public_html/backend/venv/bin"
ExecStart=/home/master/applications/[DJANGO_APP_ID]/public_html/backend/venv/bin/celery -A pavilion_gemini worker --loglevel=info --logfile=/home/master/applications/[DJANGO_APP_ID]/logs/celery-worker.log --detach
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

Create Celery Beat service:
```bash
sudo nano /etc/systemd/system/pavilion-celery-beat.service
```

Add:
```ini
[Unit]
Description=Pavilion Celery Beat
After=network.target

[Service]
Type=forking
User=master
Group=master
WorkingDirectory=/home/master/applications/[DJANGO_APP_ID]/public_html/backend
Environment="PATH=/home/master/applications/[DJANGO_APP_ID]/public_html/backend/venv/bin"
ExecStart=/home/master/applications/[DJANGO_APP_ID]/public_html/backend/venv/bin/celery -A pavilion_gemini beat --loglevel=info --logfile=/home/master/applications/[DJANGO_APP_ID]/logs/celery-beat.log --detach
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pavilion-celery
sudo systemctl enable pavilion-celery-beat
sudo systemctl start pavilion-celery
sudo systemctl start pavilion-celery-beat
```

### 8. Configure Gunicorn

Create Gunicorn configuration file:
```bash
cd /home/master/applications/[DJANGO_APP_ID]/public_html/backend
nano gunicorn_config.py
```

Add:
```python
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
```

### 9. Set Up Gunicorn Service

```bash
sudo nano /etc/systemd/system/pavilion-gunicorn.service
```

Add:
```ini
[Unit]
Description=Pavilion Gunicorn daemon
After=network.target

[Service]
User=master
Group=master
WorkingDirectory=/home/master/applications/[DJANGO_APP_ID]/public_html/backend
Environment="PATH=/home/master/applications/[DJANGO_APP_ID]/public_html/backend/venv/bin"
ExecStart=/home/master/applications/[DJANGO_APP_ID]/public_html/backend/venv/bin/gunicorn \
    --config /home/master/applications/[DJANGO_APP_ID]/public_html/backend/gunicorn_config.py \
    pavilion_gemini.wsgi:application

Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pavilion-gunicorn
sudo systemctl start pavilion-gunicorn
```

---

## React Frontend Deployment

### 1. Prepare Frontend Directory

```bash
# Navigate to frontend application directory
cd /home/master/applications/[FRONTEND_APP_ID]/public_html/

# Clone repository or upload files
git clone [your-repo-url]/pavilion-gemini.git temp
mv temp/frontend/* .
rm -rf temp
```

### 2. Build React Application

```bash
cd /home/master/applications/[FRONTEND_APP_ID]/public_html/

# Install Node.js if not available (Cloudways usually has it)
# Check version
node --version
npm --version

# Install dependencies
npm install

# Create production .env file
nano .env.production
```

Add to `.env.production`:
```env
VITE_API_BASE_URL=/super-admin/api/
```

**Important**: The API base URL should be relative (`/super-admin/api/`) so it works with the Nginx proxy.

### 3. Build for Production

```bash
# Build the application
npm run build

# The build output will be in the 'dist' directory
```

### 4. Configure Vite for Production Base Path

Update `vite.config.js` to set the base path:

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/admin/',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
})
```

Rebuild after this change:
```bash
npm run build
```

### 5. Set Up Static File Serving

The `dist` folder should be served by Nginx. We'll configure this in the Nginx section.

---

## Nginx Configuration

This is the **most critical part** - configuring Nginx to route requests correctly.

### 1. Access Nginx Configuration

In Cloudways:
1. Go to your server → **Application Management**
2. Select your WordPress application
3. Go to **Application Settings** → **Nginx Configuration**

Or via SSH:
```bash
# Nginx config location (may vary)
cd /etc/nginx/sites-available/
# Or
cd /home/master/applications/[APP_ID]/conf/nginx/
```

### 2. Main Nginx Configuration

Create or edit the main site configuration. The configuration should handle:

1. **Root domain** (`/`) → WordPress
2. **`/admin`** → React Frontend
3. **`/super-admin`** → Django Backend
4. **`/super-admin/api`** → Django API
5. **`/super-admin/media`** → Django Media files
6. **`/super-admin/static`** → Django Static files

Here's the complete Nginx configuration:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name dev.pavilionend.in www.dev.pavilionend.in;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name dev.pavilionend.in www.dev.pavilionend.in;
    
    root /home/master/applications/[WORDPRESS_APP_ID]/public_html;
    index index.php index.html index.htm;
    
    # SSL Configuration (will be set up via Cloudways SSL)
    ssl_certificate /etc/ssl/certs/cloudways.crt;
    ssl_certificate_key /etc/ssl/private/cloudways.key;
    
    # SSL Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Logging
    access_log /home/master/applications/[WORDPRESS_APP_ID]/logs/access.log;
    error_log /home/master/applications/[WORDPRESS_APP_ID]/logs/error.log;
    
    # Max upload size
    client_max_body_size 100M;
    
    # ============================================
    # React Frontend - /admin route
    # ============================================
    location /admin {
        alias /home/master/applications/[FRONTEND_APP_ID]/public_html/dist;
        try_files $uri $uri/ /admin/index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # Security headers for admin
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
    }
    
    # ============================================
    # Django Backend - /super-admin route
    # ============================================
    location /super-admin {
        # Proxy to Gunicorn
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }
    
    # Django Media files
    location /super-admin/media {
        alias /home/master/applications/[DJANGO_APP_ID]/public_html/backend/media;
        expires 30d;
        add_header Cache-Control "public";
    }
    
    # Django Static files
    location /super-admin/static {
        alias /home/master/applications/[DJANGO_APP_ID]/public_html/backend/staticfiles;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # ============================================
    # WordPress - Root and all other routes
    # ============================================
    location / {
        try_files $uri $uri/ /index.php?$args;
    }
    
    # PHP-FPM configuration for WordPress
    location ~ \.php$ {
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;  # Adjust PHP version
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param PATH_INFO $fastcgi_path_info;
    }
    
    # Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # Deny access to backup files
    location ~* \.(bak|config|sql|fla|psd|ini|log|sh|inc|swp|dist)$ {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

### 3. Update Django URLs for Subdirectory

Since Django will be served at `/super-admin`, you need to update Django settings:

In `backend/pavilion_gemini/settings.py`, add:

```python
# Force script name for subdirectory deployment
FORCE_SCRIPT_NAME = '/super-admin'
```

Or use a middleware. Create `backend/pavilion_gemini/middleware.py`:

```python
class SubdirectoryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set script name for subdirectory
        request.META['SCRIPT_NAME'] = '/super-admin'
        response = self.get_response(request)
        return response
```

Add to `MIDDLEWARE` in settings.py:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'pavilion_gemini.middleware.SubdirectoryMiddleware',  # Add this
    'corsheaders.middleware.CorsMiddleware',
    # ... rest of middleware
]
```

### 4. Update React Router Base Path

In `frontend/src/main.jsx`, update BrowserRouter:

```javascript
<BrowserRouter basename="/admin">
  <App />
</BrowserRouter>
```

### 5. Test and Reload Nginx

```bash
# Test Nginx configuration
sudo nginx -t

# If test passes, reload Nginx
sudo systemctl reload nginx
# Or via Cloudways panel: Application Settings → Restart Nginx
```

---

## Environment Variables

### Summary of Required Environment Variables

#### Django Backend (`.env` file)
- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- Database credentials
- `CORS_ALLOWED_ORIGINS`
- `REDIS_URL`
- `GEMINI_API_KEY`
- `GOOGLE_APPLICATION_CREDENTIALS`
- `NEWS_API_KEY`
- `RSS_FEEDS`

#### React Frontend (`.env.production`)
- `VITE_API_BASE_URL=/super-admin/api/`

---

## Database Setup

### PostgreSQL Setup Checklist

1. ✅ Database created: `pavilion_gemini`
2. ✅ User created with proper permissions
3. ✅ Connection tested from Django app
4. ✅ Migrations run successfully
5. ✅ Superuser created

### WordPress Database

WordPress database is automatically created during installation via Cloudways.

---

## SSL Certificate Setup

### Via Cloudways Panel (Recommended)

1. Go to your server → **SSL Certificate**
2. Click **"Let's Encrypt SSL"**
3. Enter domain: `dev.pavilionend.in`
4. Add www variant: `www.dev.pavilionend.in`
5. Click **"Install SSL"**
6. Enable **"Force HTTPS"**

### Manual SSL Setup

If using custom SSL:
1. Upload certificate files via Cloudways panel
2. Update Nginx configuration with certificate paths
3. Reload Nginx

---

## Post-Deployment Checklist

### WordPress
- [ ] Theme activated
- [ ] Permalinks configured
- [ ] Site URL set correctly
- [ ] API endpoint configured in theme
- [ ] Test homepage loads

### Django Backend
- [ ] Environment variables set
- [ ] Database connected and migrated
- [ ] Static files collected
- [ ] Media directory permissions set (755)
- [ ] Gunicorn service running
- [ ] Celery worker running
- [ ] Celery beat running
- [ ] Test API endpoint: `https://dev.pavilionend.in/super-admin/api/`
- [ ] Test admin: `https://dev.pavilionend.in/super-admin/admin/`

### React Frontend
- [ ] Build completed successfully
- [ ] Base path configured (`/admin`)
- [ ] API base URL configured (`/super-admin/api/`)
- [ ] Test frontend: `https://dev.pavilionend.in/admin`
- [ ] Test login functionality
- [ ] Test API connectivity

### Nginx
- [ ] Configuration tested (`nginx -t`)
- [ ] Nginx reloaded
- [ ] All routes working:
  - [ ] `/` → WordPress
  - [ ] `/admin` → React Frontend
  - [ ] `/super-admin` → Django Backend
  - [ ] `/super-admin/api` → Django API
  - [ ] `/super-admin/media` → Media files
  - [ ] `/super-admin/static` → Static files

### Security
- [ ] SSL certificate installed
- [ ] HTTPS redirect working
- [ ] `.env` files not accessible via web
- [ ] File permissions set correctly
- [ ] Firewall configured (if applicable)

### Monitoring
- [ ] Logs accessible
- [ ] Error logging working
- [ ] Celery tasks running
- [ ] RSS feeds fetching

---

## Troubleshooting

### Issue: 502 Bad Gateway

**Causes:**
- Gunicorn not running
- Wrong port in Nginx proxy_pass
- Permission issues

**Solutions:**
```bash
# Check Gunicorn status
sudo systemctl status pavilion-gunicorn

# Check if port 8000 is listening
netstat -tlnp | grep 8000

# Check Gunicorn logs
tail -f /home/master/applications/[DJANGO_APP_ID]/logs/gunicorn.log

# Restart Gunicorn
sudo systemctl restart pavilion-gunicorn
```

### Issue: React App Shows Blank Page

**Causes:**
- Incorrect base path
- API base URL misconfigured
- Build files not in correct location

**Solutions:**
1. Check browser console for errors
2. Verify `dist` folder exists and has files
3. Check Nginx alias path is correct
4. Verify `basename="/admin"` in BrowserRouter
5. Check API base URL in `.env.production`

### Issue: Django URLs Not Working

**Causes:**
- Subdirectory middleware not configured
- Nginx proxy headers missing
- FORCE_SCRIPT_NAME not set

**Solutions:**
1. Verify middleware is added
2. Check Nginx proxy_set_header directives
3. Test direct Gunicorn: `curl http://127.0.0.1:8000/api/`
4. Check Django ALLOWED_HOSTS includes domain

### Issue: Static/Media Files Not Loading

**Causes:**
- Incorrect file paths
- Permission issues
- Nginx alias misconfigured

**Solutions:**
```bash
# Check file permissions
ls -la /home/master/applications/[DJANGO_APP_ID]/public_html/backend/staticfiles
ls -la /home/master/applications/[DJANGO_APP_ID]/public_html/backend/media

# Fix permissions
chmod -R 755 /home/master/applications/[DJANGO_APP_ID]/public_html/backend/media
chmod -R 755 /home/master/applications/[DJANGO_APP_ID]/public_html/backend/staticfiles

# Check Nginx alias paths match actual paths
```

### Issue: CORS Errors

**Causes:**
- CORS_ALLOWED_ORIGINS not configured
- Missing credentials in requests

**Solutions:**
1. Update `.env` CORS_ALLOWED_ORIGINS:
   ```
   CORS_ALLOWED_ORIGINS=https://dev.pavilionend.in,https://www.dev.pavilionend.in
   ```
2. Restart Gunicorn after changes
3. Check browser Network tab for CORS headers

### Issue: Celery Tasks Not Running

**Causes:**
- Redis not accessible
- Celery services not running
- Wrong Redis URL

**Solutions:**
```bash
# Check Redis
redis-cli ping

# Check Celery services
sudo systemctl status pavilion-celery
sudo systemctl status pavilion-celery-beat

# Check Celery logs
tail -f /home/master/applications/[DJANGO_APP_ID]/logs/celery-worker.log
tail -f /home/master/applications/[DJANGO_APP_ID]/logs/celery-beat.log

# Restart services
sudo systemctl restart pavilion-celery
sudo systemctl restart pavilion-celery-beat
```

### Issue: WordPress API Calls Failing

**Causes:**
- API URL misconfigured in theme
- CORS issues
- SSL certificate issues

**Solutions:**
1. Check theme API configuration
2. Verify API endpoint is accessible: `https://dev.pavilionend.in/super-admin/api/`
3. Check browser console for errors
4. Verify SSL certificate is valid

---

## File Permissions Reference

```bash
# Django application
chmod 755 /home/master/applications/[DJANGO_APP_ID]/public_html/backend
chmod 644 /home/master/applications/[DJANGO_APP_ID]/public_html/backend/.env
chmod 600 /home/master/applications/[DJANGO_APP_ID]/public_html/backend/credentials/*.json

# Media and static files
chmod -R 755 /home/master/applications/[DJANGO_APP_ID]/public_html/backend/media
chmod -R 755 /home/master/applications/[DJANGO_APP_ID]/public_html/backend/staticfiles

# React frontend
chmod -R 755 /home/master/applications/[FRONTEND_APP_ID]/public_html/dist

# WordPress
chmod -R 755 /home/master/applications/[WORDPRESS_APP_ID]/public_html
chmod 644 /home/master/applications/[WORDPRESS_APP_ID]/public_html/wp-config.php
```

---

## Useful Commands Reference

```bash
# Django
cd /home/master/applications/[DJANGO_APP_ID]/public_html/backend
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser

# Gunicorn
sudo systemctl status pavilion-gunicorn
sudo systemctl restart pavilion-gunicorn
sudo systemctl stop pavilion-gunicorn
sudo systemctl start pavilion-gunicorn

# Celery
sudo systemctl status pavilion-celery
sudo systemctl restart pavilion-celery
sudo systemctl restart pavilion-celery-beat

# Nginx
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl restart nginx

# Logs
tail -f /home/master/applications/[APP_ID]/logs/error.log
tail -f /home/master/applications/[DJANGO_APP_ID]/logs/celery-worker.log

# React Build
cd /home/master/applications/[FRONTEND_APP_ID]/public_html
npm run build
```

---

## Support & Additional Resources

- **Cloudways Documentation**: https://support.cloudways.com/
- **Django Deployment**: https://docs.djangoproject.com/en/4.2/howto/deployment/
- **Gunicorn Documentation**: https://docs.gunicorn.org/
- **Nginx Documentation**: https://nginx.org/en/docs/

---

## Notes

- Replace `[APP_ID]`, `[DJANGO_APP_ID]`, `[FRONTEND_APP_ID]`, `[WORDPRESS_APP_ID]` with actual application IDs from Cloudways
- Replace `[your-repo-url]` with your actual Git repository URL
- Adjust PHP version (php8.1-fpm.sock) based on your Cloudways PHP version
- Test each component individually before testing the full integration
- Keep backups of configuration files before making changes
- Monitor logs regularly during initial deployment

---

**Last Updated**: [Current Date]
**Version**: 1.0

