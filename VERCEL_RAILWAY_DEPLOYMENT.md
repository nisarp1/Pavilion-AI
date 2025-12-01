# Vercel + Railway Deployment Guide

This guide explains how to deploy your Django backend to **Railway** and your React frontend to **Vercel**. This is a modern, scalable, and much easier setup than managing your own VPS.

## Part 1: Backend Deployment (Railway)

### 1. Push Code to GitHub
Ensure your latest changes (including `dj-database-url` and `whitenoise` updates) are pushed.

```bash
git add .
git commit -m "Configure for Railway deployment"
git push origin main
```

### 2. Create Railway Project
1.  Go to [Railway.app](https://railway.app/) and sign up/login.
2.  Click **New Project** -> **Deploy from GitHub repo**.
3.  Select your repository (`Pavilion-AI`).
4.  Click **Add Variables** (we will do this later).
5.  Click **Deploy Now**.

### 3. Configure Service (Backend)
Railway will detect the repo. We need to tell it to only look at the `backend` folder.
1.  Click on the service card (it might be named `Pavilion-AI`).
2.  Go to **Settings**.
3.  Scroll down to **Root Directory** and set it to `/backend`.
4.  **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
5.  **Start Command:** `gunicorn pavilion_gemini.wsgi`

### 4. Add Database
1.  In the Railway project view, right-click (or click "New") -> **Database** -> **PostgreSQL**.
2.  Wait for it to initialize.

### 5. Configure Environment Variables
1.  Click on your Backend Service card -> **Variables**.
2.  Add the following:
    *   `SECRET_KEY`: (Generate a random string)
    *   `DEBUG`: `False`
    *   `ALLOWED_HOSTS`: `*` (or your domain later)
    *   `DATABASE_URL`: `${{PostgreSQL.DATABASE_URL}}` (Railway auto-completes this reference).
    *   `PORT`: `8000` (Optional, Railway usually detects it).

### 6. Redeploy
Railway usually redeploys automatically when variables change. If not, click **Deploy**.
Once deployed, you will get a URL like `pavilion-ai-production.up.railway.app`.
**Copy this URL.**

---

## Part 2: Frontend Deployment (Vercel)

### 1. Import Project
1.  Go to [Vercel.com](https://vercel.com/) and sign up/login.
2.  Click **Add New...** -> **Project**.
3.  Import `Pavilion-AI` from GitHub.

### 2. Configure Build
1.  **Framework Preset:** Vite (should be auto-detected).
2.  **Root Directory:** Click Edit and select `frontend`.
3.  **Environment Variables:**
    *   `VITE_API_BASE_URL`: Paste your Railway Backend URL (e.g., `https://pavilion-ai-production.up.railway.app/api/`)
    *   **Note:** Make sure to include `/api/` at the end if your code expects it, or just the base domain depending on your `api.js`.

### 3. Deploy
Click **Deploy**. Vercel will build your React app and host it on a global CDN.

---

## Part 3: Domain Setup (dev.pavilionend.in)

### 1. Point Domain to Vercel
1.  In Vercel Project -> **Settings** -> **Domains**.
2.  Add `dev.pavilionend.in`.
3.  Vercel will give you a **CNAME** record (e.g., `cname.vercel-dns.com`).
4.  Go to your DNS Provider (Cloudflare/GoDaddy) and update the `dev` subdomain CNAME record.

### 2. Backend Domain (Optional)
If you want the backend on `api.pavilionend.in`:
1.  In Railway -> Service -> **Settings** -> **Networking** -> **Custom Domain**.
2.  Add `api.pavilionend.in`.
3.  Update DNS CNAME for `api` to point to Railway.
4.  Update `VITE_API_BASE_URL` in Vercel to `https://api.pavilionend.in/api/`.

---

## Troubleshooting

*   **CORS Error:** If frontend can't talk to backend, add your Vercel domain (`https://dev.pavilionend.in`) to `CORS_ALLOWED_ORIGINS` variable in Railway.
*   **Static Files:** If admin CSS is missing, ensure `whitenoise` is installed and `collectstatic` ran during build.
