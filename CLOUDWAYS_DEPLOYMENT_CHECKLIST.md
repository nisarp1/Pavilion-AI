# Cloudways Deployment Checklist

Use this checklist to ensure all steps are completed during deployment.

## Pre-Deployment

- [ ] Cloudways server created and accessible
- [ ] Domain DNS pointed to Cloudways server IP
- [ ] SSH access configured
- [ ] All API keys and credentials ready
- [ ] Git repository access configured

## Server Setup

- [ ] WordPress application created in Cloudways
- [ ] Django application created in Cloudways (Python)
- [ ] Frontend application created in Cloudways (Static/Node.js)
- [ ] PostgreSQL database created
- [ ] Redis service verified
- [ ] Node.js version confirmed (18+)
- [ ] Python version confirmed (3.11+)
- [ ] PHP version confirmed (8.1+)

## WordPress Deployment

- [ ] WordPress installed via Cloudways
- [ ] Pavilion theme uploaded to `/wp-content/themes/pavilion/`
- [ ] Theme activated
- [ ] Permalinks configured (Post name)
- [ ] Site URL set to `https://dev.pavilionend.in`
- [ ] WordPress admin credentials saved securely
- [ ] Test homepage loads correctly

## Django Backend Deployment

### Initial Setup
- [ ] Repository cloned to Django app directory
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Gunicorn installed (`pip install gunicorn`)

### Configuration
- [ ] `.env` file created with all variables
- [ ] `SECRET_KEY` generated and set
- [ ] `DEBUG=False` set
- [ ] `ALLOWED_HOSTS` includes domain
- [ ] Database credentials configured
- [ ] `CORS_ALLOWED_ORIGINS` includes domain
- [ ] `REDIS_URL` configured
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` path set
- [ ] Google TTS key file uploaded to `backend/credentials/`
- [ ] Key file permissions set (600)

### Database
- [ ] PostgreSQL database created
- [ ] Database user created with permissions
- [ ] Connection tested
- [ ] Migrations run (`python manage.py migrate`)
- [ ] Superuser created (`python manage.py createsuperuser`)
- [ ] Static files collected (`python manage.py collectstatic`)

### Services
- [ ] Gunicorn service file created
- [ ] Gunicorn service enabled and started
- [ ] Gunicorn running on port 8000
- [ ] Celery worker service created
- [ ] Celery worker service enabled and started
- [ ] Celery beat service created
- [ ] Celery beat service enabled and started
- [ ] All services status checked

### Middleware
- [ ] Subdirectory middleware file created
- [ ] Middleware added to `MIDDLEWARE` in settings.py
- [ ] `DJANGO_SUBDIRECTORY` environment variable set

## React Frontend Deployment

### Build Setup
- [ ] Repository cloned/uploaded to frontend app directory
- [ ] Node.js dependencies installed (`npm install`)
- [ ] `.env.production` file created
- [ ] `VITE_API_BASE_URL` set to `/super-admin/api/`
- [ ] `vite.config.js` updated with `base: '/admin/'`
- [ ] `main.jsx` updated with `basename="/admin"` in BrowserRouter

### Build
- [ ] Production build completed (`npm run build`)
- [ ] Build output verified in `dist/` directory
- [ ] Build files have correct permissions (755)

## Nginx Configuration

- [ ] Nginx configuration file created/updated
- [ ] WordPress root path configured
- [ ] `/admin` location block configured (React frontend)
- [ ] `/super-admin` location block configured (Django backend)
- [ ] `/super-admin/media` location block configured
- [ ] `/super-admin/static` location block configured
- [ ] Proxy headers configured correctly
- [ ] PHP-FPM socket path correct
- [ ] Configuration tested (`nginx -t`)
- [ ] Nginx reloaded/restarted

## SSL Certificate

- [ ] SSL certificate installed via Cloudways
- [ ] Domain verified
- [ ] HTTPS redirect configured
- [ ] SSL certificate valid and working
- [ ] Force HTTPS enabled

## Testing

### WordPress
- [ ] Homepage loads: `https://dev.pavilionend.in`
- [ ] WordPress admin accessible
- [ ] Theme displays correctly
- [ ] Permalinks working

### Django Backend
- [ ] API root accessible: `https://dev.pavilionend.in/super-admin/api/`
- [ ] Django admin accessible: `https://dev.pavilionend.in/super-admin/admin/`
- [ ] Static files loading: `https://dev.pavilionend.in/super-admin/static/...`
- [ ] Media files loading: `https://dev.pavilionend.in/super-admin/media/...`
- [ ] API endpoints responding correctly
- [ ] CORS headers present in responses

### React Frontend
- [ ] Frontend loads: `https://dev.pavilionend.in/admin`
- [ ] No console errors
- [ ] Login page displays
- [ ] API calls working (check Network tab)
- [ ] Routes working correctly
- [ ] Assets loading (JS, CSS, images)

### Integration
- [ ] WordPress can call Django API
- [ ] React frontend can authenticate
- [ ] React frontend can fetch data
- [ ] File uploads working (if applicable)
- [ ] RSS feeds fetching (check Celery logs)
- [ ] Celery tasks executing

## Security

- [ ] `.env` files not web-accessible
- [ ] File permissions set correctly
- [ ] Sensitive files denied in Nginx
- [ ] SSL certificate valid
- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] Database credentials secure
- [ ] API keys not exposed

## Monitoring & Logs

- [ ] Error logs accessible
- [ ] Access logs accessible
- [ ] Gunicorn logs accessible
- [ ] Celery logs accessible
- [ ] Nginx logs accessible
- [ ] Log rotation configured (if needed)

## Performance

- [ ] Static file caching configured
- [ ] Gzip compression enabled (if applicable)
- [ ] Database queries optimized
- [ ] Redis caching working (if applicable)
- [ ] CDN configured (if applicable)

## Backup & Recovery

- [ ] Backup strategy defined
- [ ] Database backup configured
- [ ] Media files backup configured
- [ ] Configuration files backed up
- [ ] Recovery procedure documented

## Documentation

- [ ] Deployment guide reviewed
- [ ] Configuration documented
- [ ] Credentials stored securely
- [ ] Team members have access
- [ ] Troubleshooting guide available

## Post-Deployment

- [ ] All services running
- [ ] No errors in logs
- [ ] Performance acceptable
- [ ] Monitoring alerts configured (if applicable)
- [ ] Team notified of deployment
- [ ] User acceptance testing completed

---

## Quick Verification Commands

```bash
# Check services
sudo systemctl status pavilion-gunicorn
sudo systemctl status pavilion-celery
sudo systemctl status pavilion-celery-beat

# Check ports
netstat -tlnp | grep 8000
redis-cli ping

# Check logs
tail -f /home/master/applications/[DJANGO_APP_ID]/logs/error.log
tail -f /home/master/applications/[DJANGO_APP_ID]/logs/celery-worker.log

# Test API
curl https://dev.pavilionend.in/super-admin/api/
curl https://dev.pavilionend.in/admin

# Check Nginx
sudo nginx -t
sudo systemctl status nginx
```

---

**Notes:**
- Replace `[APP_ID]` placeholders with actual Cloudways application IDs
- Keep this checklist updated as you progress
- Check off items only after verifying they work correctly
- Document any deviations or issues encountered

