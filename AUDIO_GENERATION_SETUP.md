# Audio Generation Setup for Malayalam Sports Articles

## ✅ Feature Overview

This feature automatically generates audio versions of articles using Google Cloud Text-to-Speech API when an article is generated. The audio uses:

- **Language**: Malayalam (ml-IN)
- **Voice**: Male or Female Indian voice (configurable)
- **Style**: Energetic news anchor style
- **Optimization**: Optimized for reading Malayalam sports articles

## 🔧 Prerequisites

### 1. Install Dependencies

Make sure you have installed the Google Cloud Text-to-Speech library:

```bash
cd backend
pip install google-cloud-texttospeech==2.16.3
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### 2. Set Up Google Cloud Text-to-Speech

You need to set up Google Cloud credentials for Text-to-Speech API:

#### Option A: Service Account (Recommended)

1. **Create a Google Cloud Project** (if you don't have one):
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Text-to-Speech API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Cloud Text-to-Speech API"
   - Click "Enable"

3. **Create a Service Account**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Give it a name (e.g., "tts-service")
   - Grant it the "Cloud Text-to-Speech API User" role
   - Click "Done"

4. **Download Service Account Key**:
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose JSON format
   - Download the JSON file

5. **Set Environment Variable**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
   ```

   Or add to your `.env` file:
   ```env
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
   ```

#### Option B: Default Credentials (Development)

If running on Google Cloud Platform or have run `gcloud auth application-default login`:

```bash
gcloud auth application-default login
```

This sets up default credentials automatically.

### 3. Run Database Migration

Run the migration to add the audio field to the Article model:

```bash
cd backend
source venv/bin/activate  # If using virtual environment
python manage.py migrate
```

## 🎯 How It Works

### Automatic Generation

When you generate an article using Gemini AI:

1. **Article Generation**: The article body is generated in Malayalam
2. **Audio Generation**: After the article is generated, audio is automatically created:
   - Extracts text from HTML article body
   - Uses Malayalam (ml-IN) voices (WaveNet quality)
   - Applies energetic news anchor style with SSML
   - Saves as MP3 file to `articles/audio/` directory

### Voice Configuration

By default, the system uses:
- **Gender**: Male (ml-IN-Wavenet-B)
- **Style**: Energetic news anchor
- **Settings**:
  - Speaking rate: 1.1x (slightly faster)
  - Pitch: +2 semitones (more energetic)
  - Volume: +2 dB (louder)
  - Encoding: MP3

To use a female voice, modify `backend/workers/tasks.py` in the `_generate_article_task_impl` function:

```python
generate_audio_for_article(article, voice_gender='FEMALE')
```

### Available Voices

- **ml-IN-Wavenet-A**: Female Malayalam voice (WaveNet quality)
- **ml-IN-Wavenet-B**: Male Malayalam voice (WaveNet quality)
- **ml-IN-Standard-A**: Female Malayalam voice (Standard quality, cheaper)
- **ml-IN-Standard-B**: Male Malayalam voice (Standard quality, cheaper)

## 📝 Usage

### Generating Audio Automatically

Audio is automatically generated when you:
1. Click "Generate" on a fetched article
2. The article body is populated with Malayalam content
3. Audio is created and saved automatically

### Accessing Audio

The audio file is available via the Article API:

```json
{
  "id": 123,
  "title": "Article Title",
  "audio": "/media/articles/audio/article_123_audio.mp3",
  "audio_url": "http://localhost:8000/media/articles/audio/article_123_audio.mp3"
}
```

### Manual Audio Generation

You can also generate audio manually for existing articles by calling the function directly:

```python
from cms.models import Article
from workers.tasks import generate_audio_for_article

article = Article.objects.get(id=123)
generate_audio_for_article(article, voice_gender='MALE')
```

## 🔍 Troubleshooting

### Audio Not Generated

1. **Check Dependencies**:
   ```bash
   pip list | grep texttospeech
   ```
   Should show `google-cloud-texttospeech==2.16.3`

2. **Check Credentials**:
   ```bash
   echo $GOOGLE_APPLICATION_CREDENTIALS
   ```
   Should show the path to your service account JSON file

3. **Check Logs**:
   Look for these log messages:
   - "Starting audio generation for article {id}"
   - "Audio generated successfully for article {id}"
   - Or error messages if something fails

### Common Errors

1. **"Credentials not configured"**:
   - Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable
   - Or run `gcloud auth application-default login`

2. **"Permission denied"**:
   - Make sure the service account has "Cloud Text-to-Speech API User" role
   - Check that the Text-to-Speech API is enabled in your project

3. **"Quota exceeded"**:
   - Check your Google Cloud billing
   - Verify API quota limits in Cloud Console

4. **"Voice not found"**:
   - Verify that WaveNet voices are available in your region
   - Consider using Standard voices if WaveNet is unavailable

### API Limits

- **Text Length**: Max 5000 characters per request (articles are truncated to 4800 chars)
- **Rate Limits**: Check [Google Cloud TTS quotas](https://cloud.google.com/text-to-speech/quotas)
- **Costs**: WaveNet voices cost more than Standard voices

## 🎨 Customization

### Changing Voice Style

Edit `backend/workers/tasks.py` in the `generate_audio_for_article` function:

```python
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=1.2,  # Change speed (0.25 to 4.0)
    pitch=4.0,  # Change pitch (-20.0 to 20.0 semitones)
    volume_gain_db=3.0,  # Change volume (-96.0 to 16.0 dB)
)
```

### Using Standard Voices (Cheaper)

Change voice selection:

```python
if voice_gender.upper() == 'FEMALE':
    voice_name = 'ml-IN-Standard-A'  # Standard female voice
else:
    voice_name = 'ml-IN-Standard-B'  # Standard male voice
```

## 📚 Additional Resources

- [Google Cloud Text-to-Speech Documentation](https://cloud.google.com/text-to-speech/docs)
- [Available Voices](https://cloud.google.com/text-to-speech/docs/voices)
- [SSML Reference](https://cloud.google.com/text-to-speech/docs/ssml)
- [Pricing Information](https://cloud.google.com/text-to-speech/pricing)

## ✅ Verification

After setup, verify it's working:

1. Generate a new article
2. Check the backend logs for "Audio generated successfully"
3. Check the article in the API response for `audio_url` field
4. Download and play the audio file to verify quality

---

**Note**: Audio generation happens automatically after article generation. If article generation fails, audio generation is skipped.

