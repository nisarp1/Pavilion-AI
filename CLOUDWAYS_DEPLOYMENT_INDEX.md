# Cloudways Deployment Documentation Index

Complete guide for deploying Pavilion projects to Cloudways under `dev.pavilionend.in`.

## 📚 Documentation Files

### 1. **CLOUDWAYS_DEPLOYMENT_GUIDE.md** ⭐ START HERE
   **Comprehensive step-by-step deployment guide**
   - Complete setup instructions
   - Detailed configuration for all components
   - Troubleshooting section
   - **Read this first for full understanding**

### 2. **CLOUDWAYS_QUICK_START.md** 🚀
   **Quick reference guide**
   - Condensed version for experienced users
   - Essential commands and configurations
   - Quick troubleshooting tips
   - **Use this as a quick reference**

### 3. **CLOUDWAYS_DEPLOYMENT_CHECKLIST.md** ✅
   **Deployment checklist**
   - Step-by-step checklist
   - Verification commands
   - Post-deployment testing
   - **Use this to track your progress**

### 4. **CLOUDWAYS_CODE_UPDATES.md** 💻
   **Required code changes**
   - Specific code modifications needed
   - File-by-file instructions
   - Testing instructions
   - **Review before deploying**

### 5. **CLOUDWAYS_NGINX_CONFIG.conf** ⚙️
   **Nginx configuration template**
   - Complete Nginx configuration
   - Ready to customize with your app IDs
   - Routing for all three applications
   - **Use this as your Nginx config template**

### 6. **CLOUDWAYS_ENV_TEMPLATE.txt** 🔐
   **Environment variables template**
   - Django backend `.env` template
   - React frontend `.env.production` template
   - All required variables documented
   - **Copy and fill in your values**

## 🎯 Deployment Architecture

```
dev.pavilionend.in
│
├── / (root)
│   └── WordPress (pavilion-theme)
│       └── Serves main website
│
├── /admin
│   └── React Frontend (pavilion-gemini frontend)
│       └── Admin dashboard for content management
│
└── /super-admin
    └── Django Backend (pavilion-gemini backend)
        ├── /api → REST API endpoints
        ├── /admin → Django admin panel
        ├── /media → Media files
        └── /static → Static files
```

## 🚀 Quick Start Workflow

1. **Read**: `CLOUDWAYS_DEPLOYMENT_GUIDE.md` (full guide)
2. **Review**: `CLOUDWAYS_CODE_UPDATES.md` (code changes needed)
3. **Prepare**: Update code locally with required changes
4. **Setup**: Follow `CLOUDWAYS_DEPLOYMENT_CHECKLIST.md` step by step
5. **Configure**: Use `CLOUDWAYS_NGINX_CONFIG.conf` for Nginx
6. **Deploy**: Use `CLOUDWAYS_ENV_TEMPLATE.txt` for environment variables
7. **Reference**: Use `CLOUDWAYS_QUICK_START.md` for quick commands

## 📋 Pre-Deployment Checklist

Before starting, ensure you have:

- [ ] Cloudways account with server created
- [ ] Domain `dev.pavilionend.in` DNS pointed to Cloudways IP
- [ ] SSH access to Cloudways server
- [ ] Git repository access
- [ ] All API keys ready:
  - [ ] Google Gemini API key
  - [ ] Google Cloud TTS credentials (JSON file)
  - [ ] News API key
  - [ ] AWS credentials (if using S3)
- [ ] Database credentials (will create in Cloudways)
- [ ] Code changes applied locally (see `CLOUDWAYS_CODE_UPDATES.md`)

## 🔧 Key Components

### Applications Needed

1. **WordPress Application**
   - Type: WordPress
   - Domain: `dev.pavilionend.in`
   - PHP: 8.1+

2. **Django Application**
   - Type: Python/Django
   - Domain: `dev.pavilionend.in/super-admin`
   - Python: 3.11+
   - Database: PostgreSQL
   - Queue: Redis + Celery

3. **Frontend Application**
   - Type: Static Site or Node.js
   - Domain: `dev.pavilionend.in/admin`
   - Node.js: 18+

### Services Required

- **PostgreSQL**: Database for Django
- **Redis**: Task queue for Celery
- **Nginx**: Web server (managed by Cloudways)
- **Gunicorn**: WSGI server for Django
- **Celery**: Task queue worker
- **Celery Beat**: Scheduled tasks

## 📝 Code Changes Summary

Before deploying, make these code changes:

1. ✅ **Created**: `backend/pavilion_gemini/subdirectory_middleware.py`
2. ⚠️ **Update**: `backend/pavilion_gemini/settings.py` - Add middleware
3. ⚠️ **Update**: `frontend/src/main.jsx` - Add basename to BrowserRouter
4. ⚠️ **Update**: `frontend/vite.config.js` - Add base path

See `CLOUDWAYS_CODE_UPDATES.md` for detailed instructions.

## 🗂️ File Structure on Server

```
/home/master/applications/
├── [WORDPRESS_APP_ID]/
│   └── public_html/          → WordPress root
│       └── wp-content/themes/pavilion/  → Theme files
│
├── [DJANGO_APP_ID]/
│   └── public_html/
│       └── backend/          → Django project
│           ├── .env          → Environment variables
│           ├── venv/         → Virtual environment
│           ├── media/        → Media files
│           └── staticfiles/ → Static files
│
└── [FRONTEND_APP_ID]/
    └── public_html/
        ├── dist/             → Built React app
        └── .env.production   → Environment variables
```

## 🔗 Important URLs

After deployment, these URLs should work:

- **WordPress**: `https://dev.pavilionend.in`
- **React Admin**: `https://dev.pavilionend.in/admin`
- **Django API**: `https://dev.pavilionend.in/super-admin/api/`
- **Django Admin**: `https://dev.pavilionend.in/super-admin/admin/`

## ⚡ Quick Commands Reference

```bash
# Django
cd backend && source venv/bin/activate
python manage.py migrate
python manage.py collectstatic

# Services
sudo systemctl restart pavilion-gunicorn
sudo systemctl restart pavilion-celery

# Nginx
sudo nginx -t
sudo systemctl reload nginx

# React
npm run build

# Logs
tail -f /home/master/applications/[APP_ID]/logs/error.log
```

## 🆘 Getting Help

1. **Check**: `CLOUDWAYS_DEPLOYMENT_GUIDE.md` → Troubleshooting section
2. **Verify**: `CLOUDWAYS_DEPLOYMENT_CHECKLIST.md` → Ensure all steps completed
3. **Review**: Logs in `/home/master/applications/[APP_ID]/logs/`
4. **Test**: Each component individually before integration

## 📞 Support Resources

- Cloudways Support: https://support.cloudways.com/
- Django Deployment: https://docs.djangoproject.com/en/4.2/howto/deployment/
- Gunicorn Docs: https://docs.gunicorn.org/
- Nginx Docs: https://nginx.org/en/docs/

## 🎓 Learning Path

**For First-Time Deployment:**
1. Read `CLOUDWAYS_DEPLOYMENT_GUIDE.md` completely
2. Review `CLOUDWAYS_CODE_UPDATES.md`
3. Make code changes locally
4. Follow `CLOUDWAYS_DEPLOYMENT_CHECKLIST.md` step by step
5. Use `CLOUDWAYS_QUICK_START.md` for quick commands

**For Experienced Users:**
1. Skim `CLOUDWAYS_DEPLOYMENT_GUIDE.md`
2. Use `CLOUDWAYS_QUICK_START.md` as primary reference
3. Follow `CLOUDWAYS_DEPLOYMENT_CHECKLIST.md` for verification
4. Reference specific sections in main guide as needed

## ✅ Post-Deployment

After successful deployment:

1. Test all URLs
2. Verify all services running
3. Check logs for errors
4. Test API connectivity
5. Verify file uploads/downloads
6. Test scheduled tasks (Celery)
7. Monitor performance
8. Set up backups
9. Configure monitoring/alerts

---

**Last Updated**: [Current Date]
**Version**: 1.0

**Start with**: `CLOUDWAYS_DEPLOYMENT_GUIDE.md` for comprehensive instructions.

