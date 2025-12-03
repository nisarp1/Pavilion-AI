# Backup & Restore Guide - Stable Release v1.0

**Date:** December 3, 2025
**Status:** Stable (Gemini Generation, Voice, Images, Admin Styles all working)

## 1. How to Save this State (Tagging)
To mark this exact moment in history as "Stable v1.0", run these commands in your terminal:

```bash
# 1. Tag the current commit
git tag -a v1.0-stable -m "Stable release: Gemini, Voice, Images, Admin fixed"

# 2. Push the tag to GitHub
git push origin v1.0-stable
```

## 2. How to Restore this State
If future development breaks everything, you can revert to this version:

### Option A: View code (Safe)
To just look at the code from this version:
```bash
git checkout v1.0-stable
```
(To go back to latest: `git checkout main`)

### Option B: Hard Reset (Destructive)
To force your codebase back to this state (WARNING: deletes newer work):
```bash
git reset --hard v1.0-stable
git push origin main --force
```

## 3. Critical Railway Variables
If you delete your Railway project, you must re-add these variables for the code to work:

| Variable | Value / Note |
|----------|--------------|
| `GEMINI_API_KEY` | Your AIza... key |
| `GEMINI_MODEL` | `gemini-2.5-flash` (or `gemini-pro`) |
| `GOOGLE_CREDENTIALS_JSON` | **CRITICAL:** The full content of `google-tts-key.json` |
| `NEWS_API_KEY` | Your NewsAPI key |
| `DJANGO_SUPERUSER_USERNAME` | admin |
| `DJANGO_SUPERUSER_PASSWORD` | (Your password) |
| `DJANGO_SUPERUSER_EMAIL` | admin@example.com |
| `CORS_ALLOWED_ORIGINS` | `https://pavilion-ai.vercel.app,http://localhost:5173` |
| `CSRF_TRUSTED_ORIGINS` | `https://pavilion-ai-production.up.railway.app` |

## 4. Known Limitations
1.  **Images are Temporary:** On Railway, images disappear after redeployment. Use AWS S3 for permanent storage.
2.  **Generation is Slow:** It runs synchronously (user waits 10-20s). Future upgrade: Celery.
