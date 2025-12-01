# Three Best Malayalam Voices for News Reading

## 🎙️ Available Voices

The system now supports three premium voices for Malayalam news reading:

### 1. 🥇 **Chirp Voice** (Best Quality)
- **Voice ID**: `ml-IN-Chirp3-HD-Despina`
- **Quality**: Highest - Most natural and accurate
- **Best for**: Professional news broadcasting
- **Usage**: `voice_name='chirp'` or `voice_name='best'`

### 2. 🥈 **Neural2 Voice** (High Quality)
- **Voice ID**: `ml-IN-Neural2-A`
- **Quality**: High - Excellent prosody and naturalness
- **Best for**: Natural-sounding news narration
- **Usage**: `voice_name='neural2'` or `voice_name='premium'`

### 3. 🥉 **WaveNet Voice** (Premium Quality - Current Default)
- **Voice ID**: `ml-IN-Wavenet-A`
- **Quality**: Premium - Widely available and stable
- **Best for**: High-quality audio production
- **Usage**: `voice_name='wavenet'` or `voice_name='karthika'`

## 🔄 Automatic Fallback System

The system includes intelligent fallback:
1. **First**: Tries the requested voice (e.g., Chirp)
2. **Second**: Falls back to WaveNet if Chirp unavailable
3. **Third**: Falls back to Standard if WaveNet unavailable

This ensures audio generation always succeeds even if premium voices aren't available.

## 📝 How to Use

### In Code:
```python
# Use best quality voice (Chirp)
generate_audio_for_article(article, voice_name='chirp')

# Use high quality voice (Neural2)
generate_audio_for_article(article, voice_name='neural2')

# Use premium quality voice (WaveNet - current default)
generate_audio_for_article(article, voice_name='wavenet')
# or
generate_audio_for_article(article, voice_name='karthika')
```

### Current Default:
The system currently uses `'karthika'` which maps to `ml-IN-Wavenet-A` (WaveNet voice).

## 🎯 Recommendations

- **For best quality**: Use `'chirp'` (if available in your Google Cloud project)
- **For high quality**: Use `'neural2'` (if available)
- **For reliable quality**: Use `'wavenet'` or `'karthika'` (current default)

## 🔍 Testing

To test different voices:
1. Generate an article
2. Check logs to see which voice was used
3. Compare audio quality
4. Choose the best voice for your needs

## 📊 Voice Comparison

| Voice | Quality | Naturalness | Availability | Cost |
|-------|---------|-------------|--------------|------|
| Chirp | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Limited | Highest |
| Neural2 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Good | High |
| WaveNet | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Excellent | Medium |

---

**Note**: Chirp and Neural2 voices may require specific Google Cloud project settings. WaveNet is the most widely available premium option.

