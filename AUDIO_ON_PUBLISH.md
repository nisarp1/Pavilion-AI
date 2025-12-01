# Audio Generation on Publish

## Overview

Audio generation has been updated to **only generate audio for published articles**, not for drafts. This saves costs by avoiding audio generation for articles that may never be published.

## Changes Made

### 1. Removed Audio Generation from Article Generation Task

**File**: `backend/workers/tasks.py`

- Audio generation is no longer triggered during article generation (when status is 'draft')
- This prevents generating audio for articles that may be edited or never published

### 2. Added Signal Handler for Published Articles

**File**: `backend/cms/models.py`

- Added `generate_audio_on_publish` signal handler
- Triggers automatically when an article status changes to 'published'
- Generates audio using Chirp voice (best quality)

### 3. Status Change Tracking

**File**: `backend/cms/models.py` (Article.save method)

- Tracks status changes to detect when an article is published
- Used by signal handler to determine when to generate audio

## How It Works

1. **Article Generated**: Article is created with status='draft' (no audio generated)
2. **Article Published**: When status changes to 'published', signal triggers
3. **Audio Generated**: Signal handler automatically generates audio with Chirp voice
4. **Audio Saved**: Audio file is saved to article.audio field

## Triggers for Audio Generation

Audio is generated when:
- ✅ Article status changes from any status to 'published'
- ✅ New article is created with status='published'
- ✅ Article is published via `publish()` method
- ✅ Article is published via API endpoint (`POST /api/articles/{id}/publish/`)
- ✅ Article status is updated to 'published' via bulk update

## Cost Savings

**Before**: Audio generated for all articles (drafts + published)
- 100 drafts × $0.075 = $7.50
- 20 published × $0.075 = $1.50
- **Total**: $9.00

**After**: Audio generated only for published articles
- 100 drafts × $0 = $0
- 20 published × $0.075 = $1.50
- **Total**: $1.50

**Savings**: ~83% reduction in audio generation costs

## Manual Audio Generation

You can still manually generate audio for any article (including drafts) using:

```bash
POST /api/articles/{id}/generate_audio/
{
  "voice_name": "chirp" | "neural2" | "wavenet"
}
```

## Testing

1. **Generate Article**: Create a draft article (no audio should be generated)
2. **Publish Article**: Change status to 'published' (audio should be generated automatically)
3. **Check Audio**: Verify `article.audio` field is populated

## Logs

Check logs for audio generation:
- Success: `Article {id} published - generating audio with Chirp voice`
- Errors: `Error generating audio for published article {id}: {error}`

## Notes

- Audio generation happens synchronously (blocks until complete)
- If audio generation fails, article is still published (error is logged)
- Audio is only generated if article has body content
- Existing audio is not regenerated (only generates if audio field is empty)

