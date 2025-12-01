# Google Cloud Text-to-Speech Service Account Setup

## Step-by-Step Instructions

Since you'll be using a **Service Account** (the only option), follow these steps:

### Step 1: Create Google Cloud Project (if needed)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown (top bar)
3. Click "New Project"
4. Enter project name: `pavilion-audio` (or any name)
5. Click "Create"

### Step 2: Enable Text-to-Speech API

1. In your Google Cloud project, go to: **APIs & Services** > **Library**
2. Search for: `Cloud Text-to-Speech API`
3. Click on it and click **"Enable"** button
4. Wait for it to enable (takes a few seconds)

### Step 3: Create Service Account

1. Go to: **APIs & Services** > **Credentials**
2. Click **"+ CREATE CREDENTIALS"** dropdown at the top
3. Select **"Service account"**
4. Fill in:
   - **Service account name**: `tts-service`
   - **Service account ID**: (auto-filled, can leave as is)
   - **Description**: `Text-to-Speech service for article audio generation`
5. Click **"Create and Continue"**
6. In **"Grant this service account access to project"**:
   - Click **"Select a role"** dropdown
   - Search for: `Text-to-Speech`
   - Select: **"Cloud Text-to-Speech API User"**
7. Click **"Continue"** then **"Done"**

### Step 4: Download Service Account Key

1. You should see the service account listed under **"Service Accounts"**
2. Click on the service account name (`tts-service`)
3. Go to the **"Keys"** tab
4. Click **"Add Key"** > **"Create new key"**
5. Select **"JSON"** format
6. Click **"Create"** - this will download a JSON file
7. **IMPORTANT**: Save this file in a secure location on your computer
   - Example location: `~/Downloads/pavilion-tts-key.json`
   - Or: `/Users/nisar/Documents/pavilion-tts-key.json`

### Step 5: Add Credentials to .env File

1. Note the **full path** to your downloaded JSON file
2. Open the `.env` file in the backend directory:
   ```bash
   cd /Applications/MAMP/htdocs/pavilion-gemini/backend
   nano .env
   ```
   (Or use your preferred text editor)

3. Add this line to the `.env` file:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=/full/path/to/your/downloaded-key.json
   ```
   
   **Example** (replace with your actual path):
   ```
   GOOGLE_APPLICATION_CREDENTIALS=/Users/nisar/Downloads/pavilion-tts-key.json
   ```

4. Save and close the file

### Step 6: Verify Setup

1. Make sure the JSON file exists at the path you specified:
   ```bash
   ls -la /Users/nisar/Downloads/pavilion-tts-key.json
   ```
   (Replace with your actual path)

2. Test the import:
   ```bash
   cd /Applications/MAMP/htdocs/pavilion-gemini/backend
   source venv/bin/activate
   python -c "from google.cloud import texttospeech; client = texttospeech.TextToSpeechClient(); print('✅ Service account credentials working!')"
   ```

### Step 7: Test Audio Generation

1. Start your Django server (if not running):
   ```bash
   cd /Applications/MAMP/htdocs/pavilion-gemini/backend
   source venv/bin/activate
   python manage.py runserver 0.0.0.0:8000
   ```

2. Generate an article using the frontend
3. Check the logs - you should see:
   - "Starting audio generation for article {id}"
   - "Audio generated successfully for article {id}"

## ⚠️ Important Security Notes

- **DO NOT** commit the JSON key file to Git
- **DO NOT** share the JSON key file publicly
- Keep the JSON file in a secure location
- The `.env` file should already be in `.gitignore` (check to confirm)

## 🎯 Quick Checklist

- [ ] Google Cloud project created
- [ ] Text-to-Speech API enabled
- [ ] Service account created (`tts-service`)
- [ ] Service account granted "Cloud Text-to-Speech API User" role
- [ ] JSON key file downloaded
- [ ] JSON key saved in secure location
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` added to `.env` file
- [ ] Path in `.env` is the **full absolute path** to the JSON file
- [ ] Test import successful

## 📝 Example .env Configuration

Your `.env` file should look something like this:

```env
# Database (existing)
DB_ENGINE=sqlite3
...

# Gemini AI (existing)
GEMINI_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-2.5-flash

# Google Cloud Text-to-Speech (NEW)
GOOGLE_APPLICATION_CREDENTIALS=/Users/nisar/Downloads/pavilion-tts-key.json
```

## 🆘 Troubleshooting

### Error: "Could not find the default credentials"
- Make sure `GOOGLE_APPLICATION_CREDENTIALS` is set in `.env`
- Use the **full absolute path** (starting with `/`)
- Verify the file exists: `ls -la /path/to/file.json`

### Error: "Permission denied"
- Make sure the service account has "Cloud Text-to-Speech API User" role
- Check that Text-to-Speech API is enabled

### Error: "Invalid JSON"
- Make sure the downloaded file is valid JSON
- Check file permissions: `chmod 600 /path/to/file.json`

---

Once you complete these steps, audio generation will work automatically! 🎉

