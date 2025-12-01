# Code Updates Required for Cloudways Deployment

This document lists the specific code changes needed in your codebase for Cloudways deployment.

## 1. Django Settings Update

**File**: `backend/pavilion_gemini/settings.py`

Add the subdirectory middleware to the `MIDDLEWARE` list:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'pavilion_gemini.subdirectory_middleware.SubdirectoryMiddleware',  # ADD THIS LINE
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

**Note**: The `subdirectory_middleware.py` file has been created in `backend/pavilion_gemini/`.

## 2. React main.jsx Update

**File**: `frontend/src/main.jsx`

Update the BrowserRouter to include the `basename` prop:

```javascript
import React from 'react'
import ReactDOM from 'react-dom/client'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { store } from './store'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Provider store={store}>
      <BrowserRouter basename="/admin">  {/* ADD basename="/admin" */}
        <App />
      </BrowserRouter>
    </Provider>
  </React.StrictMode>,
)
```

## 3. React vite.config.js Update

**File**: `frontend/vite.config.js`

Add the `base` configuration for production builds:

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/admin/',  // ADD THIS LINE for production deployment
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
})
```

**Note**: The `base: '/admin/'` is only needed for production. You can make it conditional:

```javascript
export default defineConfig({
  plugins: [react()],
  base: process.env.NODE_ENV === 'production' ? '/admin/' : '/',
  // ... rest
})
```

## 4. Environment Variables

### Django Backend

Create `.env` file in `backend/` directory with production values (see `CLOUDWAYS_ENV_TEMPLATE.txt`).

**Important variables:**
- `DEBUG=False`
- `ALLOWED_HOSTS=dev.pavilionend.in,www.dev.pavilionend.in`
- `CORS_ALLOWED_ORIGINS=https://dev.pavilionend.in,https://www.dev.pavilionend.in`
- `DJANGO_SUBDIRECTORY=/super-admin`

### React Frontend

Create `.env.production` file in `frontend/` directory:

```
VITE_API_BASE_URL=/super-admin/api/
```

## 5. Django URLs Configuration (Optional Enhancement)

**File**: `backend/pavilion_gemini/urls.py`

The current URL configuration should work, but you may want to ensure all URLs are properly prefixed. The middleware handles this automatically, but you can also add:

```python
# In settings.py, you can optionally set:
FORCE_SCRIPT_NAME = '/super-admin'
```

However, the middleware approach is more flexible and recommended.

## 6. Static Files Configuration

**File**: `backend/pavilion_gemini/settings.py`

Ensure static files are configured correctly:

```python
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'  # This will be served at /super-admin/static/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'  # This will be served at /super-admin/media/
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

The Nginx configuration handles the `/super-admin/static` and `/super-admin/media` paths.

## Summary of Changes

1. ✅ **Created**: `backend/pavilion_gemini/subdirectory_middleware.py`
2. ⚠️ **Update**: `backend/pavilion_gemini/settings.py` - Add middleware to MIDDLEWARE list
3. ⚠️ **Update**: `frontend/src/main.jsx` - Add `basename="/admin"` to BrowserRouter
4. ⚠️ **Update**: `frontend/vite.config.js` - Add `base: '/admin/'` for production
5. ⚠️ **Create**: `backend/.env` - Production environment variables
6. ⚠️ **Create**: `frontend/.env.production` - Production API base URL

## Testing Locally Before Deployment

Before deploying to Cloudways, you can test these changes locally:

1. **Test Django subdirectory**:
   ```bash
   cd backend
   source venv/bin/activate
   export DJANGO_SUBDIRECTORY=/super-admin
   python manage.py runserver
   # Access at http://localhost:8000/super-admin/api/
   ```

2. **Test React with base path**:
   ```bash
   cd frontend
   npm run build
   # Serve dist folder and test routing
   ```

## Deployment Order

1. Make code changes locally
2. Test locally if possible
3. Commit changes to Git
4. Deploy to Cloudways:
   - Deploy Django backend first
   - Deploy React frontend second
   - Configure Nginx last
5. Test all routes

---

**Note**: These changes are backward compatible for local development if you use environment variables or conditional configuration.

