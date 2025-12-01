# 🚀 Quick Setup: Google Cloud Text-to-Speech Service Account

## ✅ What's Already Done
- ✅ Code installed and configured
- ✅ Database migration applied
- ✅ Dependencies installed

## 🔧 What You Need To Do (5 minutes)

### Step 1: Create Service Account in Google Cloud
1. Go to: https://console.cloud.google.com/
2. Create/Select a project
3. Enable "Cloud Text-to-Speech API" (APIs & Services > Library)
4. Go to: APIs & Services > Credentials
5. Click "Create Credentials" > "Service account"
6. Name: `tts-service`
7. Grant role: "Cloud Text-to-Speech API User"
8. Click "Keys" tab > "Add Key" > "Create new key" > JSON
9. Download the JSON file

### Step 2: Add to .env File
Open: `/Applications/MAMP/htdocs/pavilion-gemini/backend/.env`

Add this line (replace with your actual path):
```
GOOGLE_APPLICATION_CREDENTIALS=/Users/yourusername/Downloads/pavilion-tts-key.json
```

### Step 3: Restart Django Server
If your server is running, restart it to load the new credentials.

### Step 4: Test
Generate an article and check logs for "Audio generated successfully"!

## 📚 Full Instructions
See: `GOOGLE_CLOUD_SETUP_STEPS.md`
