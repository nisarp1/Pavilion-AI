# Hosting Setup Guide for dev.pavilionend.in

This guide details the steps to host your application with the following structure:
- **Root**: `dev.pavilionend.in` (Existing site)
- **Frontend**: `dev.pavilionend.in/admin` (React App)
- **Backend**: `dev.pavilionend.in/super-admin` (Django App)

## 1. Backend Configuration (Django)

We have updated `settings.py` to support subdirectory deployment via the `FORCE_SCRIPT_NAME` environment variable.

### Action Required: Update Environment Variables
On your Cloudways server, update the `.env` file for your Django application:

```env
# Add this line to handle the /super-admin path
FORCE_SCRIPT_NAME=/super-admin

# Ensure these are set correctly
ALLOWED_HOSTS=dev.pavilionend.in
CORS_ALLOWED_ORIGINS=https://dev.pavilionend.in
```

## 2. Frontend Configuration (React)

We have updated `vite.config.js` and `main.jsx` to serve the app from `/admin`.

### Action Required: Build for Production
1. Create/Update `.env.production` in your frontend directory:
   ```env
   VITE_API_BASE_URL=/super-admin/api/
   ```

2. Build the application:
   ```bash
   npm run build
   ```
   This will generate the `dist` folder which Nginx will serve.

## 3. Nginx Configuration

You need to configure Nginx to route traffic to the correct applications.

### Action Required: Update Nginx Config
In Cloudways (Application Settings -> Nginx Configuration), use the following configuration block inside your `server` block:

```nginx
    # ============================================
    # React Frontend - /admin route
    # ============================================
    location /admin {
        # Point this to your React 'dist' folder absolute path
        alias /home/master/applications/[YOUR_APP_ID]/public_html/frontend/dist;
        try_files $uri $uri/ /admin/index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # ============================================
    # Django Backend - /super-admin route
    # ============================================
    location /super-admin {
        # Proxy to Gunicorn (ensure Gunicorn is running on port 8000)
        proxy_pass http://127.0.0.1:8000;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeouts for long-running requests
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # ============================================
    # Django Static & Media Files
    # ============================================
    location /super-admin/static {
        alias /home/master/applications/[YOUR_APP_ID]/public_html/backend/staticfiles;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /super-admin/media {
        alias /home/master/applications/[YOUR_APP_ID]/public_html/backend/media;
        expires 30d;
    }
```

**Note:** Replace `[YOUR_APP_ID]` with your actual Cloudways application ID (folder name).

## 4. Verification

After applying these changes and restarting Nginx:

1. **Frontend**: Visit `https://dev.pavilionend.in/admin`
   - Should load the React app.
   - Login should direct to `/super-admin/api/...`

2. **Backend Admin**: Visit `https://dev.pavilionend.in/super-admin/admin/`
   - Should load the Django Admin login.

3. **API**: Visit `https://dev.pavilionend.in/super-admin/api/`
   - Should show the API root.
