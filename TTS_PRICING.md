# Google Cloud Text-to-Speech Pricing Guide

## Voice Pricing Comparison (2024)

### Premium Voices (Best Quality)

| Voice Type | Price per 1M Characters | Quality | Best For |
|------------|-------------------------|---------|----------|
| **Chirp 3: HD** | **$30** | ⭐⭐⭐⭐⭐ Highest | News reading, professional content |
| **Neural2** | **$20** | ⭐⭐⭐⭐ High | General purpose, excellent prosody |
| **WaveNet** | **$16** | ⭐⭐⭐⭐ Premium | Widely available, good quality |

### Standard Voices (Lower Cost)

| Voice Type | Price per 1M Characters | Quality | Best For |
|------------|-------------------------|---------|----------|
| **Standard** | **$4** | ⭐⭐⭐ Basic | Cost-effective, simple use cases |

## Cost Comparison

**Chirp vs WaveNet:**
- Chirp costs **87.5% more** than WaveNet ($30 vs $16)
- Chirp: **$30 per 1 million characters**
- WaveNet: **$16 per 1 million characters**

**Example Costs:**
- 1,000 articles × ~2,000 characters each = 2M characters
  - Chirp: **$60**
  - WaveNet: **$32**
  - Standard: **$8**

## Free Tier

Google Cloud provides:
- **First 0-4 million characters per month**: **FREE**
- After free tier: Pay per million characters

## Current Default Voice

**Chirp** (`ml-IN-Chirp3-HD-Despina`) is set as the default voice because:
- ✅ Most accurate and natural for Malayalam news reading
- ✅ Best prosody and pronunciation
- ✅ Highest quality output

## Cost Optimization Tips

### 1. Use Chirp for Important Content
- Use Chirp for published articles
- Use WaveNet for drafts/previews

### 2. Monitor Usage
- Check Google Cloud Console for monthly usage
- Set up billing alerts

### 3. Consider Voice Selection
- **Chirp**: Best quality, highest cost ($30/1M chars)
- **Neural2**: Great balance ($20/1M chars)
- **WaveNet**: Good quality, lower cost ($16/1M chars)
- **Standard**: Basic quality, lowest cost ($4/1M chars)

### 4. Text Truncation
- Articles are automatically truncated to ~4000 characters
- This helps control costs per article
- Average article: ~2,000-3,000 characters after truncation

## Cost Calculation

**Per Article Estimate:**
- Average article length: ~2,500 characters
- Chirp cost: 2,500 / 1,000,000 × $30 = **$0.075 per article**
- WaveNet cost: 2,500 / 1,000,000 × $16 = **$0.04 per article**

**Monthly Estimate (100 articles):**
- Chirp: 100 × $0.075 = **$7.50/month**
- WaveNet: 100 × $0.04 = **$4.00/month**

## Changing Default Voice

To change the default voice, edit `backend/workers/tasks.py`:

```python
# In _generate_article_task_impl function
generate_audio_for_article(article, voice_name='chirp')  # Current: Chirp
# Change to:
generate_audio_for_article(article, voice_name='wavenet')  # WaveNet (cheaper)
# Or:
generate_audio_for_article(article, voice_name='neural2')  # Neural2 (balanced)
```

## Voice Quality Ranking

1. **🥇 Chirp 3: HD** - Most natural, best for news ($30/1M)
2. **🥈 Neural2** - Excellent prosody ($20/1M)
3. **🥉 WaveNet** - Premium quality ($16/1M)
4. **Standard** - Basic quality ($4/1M)

## Recommendation

**For Production (News Site):**
- Use **Chirp** for best quality and accuracy
- Worth the extra cost for professional content
- Free tier covers first 4M characters/month

**For Development/Testing:**
- Use **WaveNet** or **Standard** to save costs
- Switch to Chirp before publishing

## References

- [Google Cloud TTS Pricing](https://cloud.google.com/text-to-speech/pricing)
- Current pricing as of 2024
- Prices may vary by region

