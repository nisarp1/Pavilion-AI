# Voice Pricing Comparison - Google Cloud Text-to-Speech

## 📊 Quick Comparison Table

| Voice Type | Price per 1M Characters | Quality Rating | Best For | Cost vs WaveNet |
|------------|------------------------|----------------|----------|-----------------|
| **🥇 Chirp 3: HD** | **$30** | ⭐⭐⭐⭐⭐ Highest | Professional news, premium content | +87.5% more expensive |
| **🥈 Neural2** | **$20** | ⭐⭐⭐⭐ High | Natural narration, excellent prosody | +25% more expensive |
| **🥉 WaveNet** | **$16** | ⭐⭐⭐⭐ Premium | High-quality, widely available | Baseline (current default) |
| **Standard** | **$4** | ⭐⭐⭐ Basic | Cost-effective, simple use cases | -75% cheaper |

---

## 💰 Detailed Pricing Breakdown

### Premium Voices

#### 1. Chirp 3: HD Voice
- **Price**: $30 per 1 million characters
- **Quality**: Highest quality, most natural
- **Best For**: 
  - Professional news broadcasting
  - Premium content
  - When quality is paramount
- **Voice ID**: `ml-IN-Chirp3-HD-Despina`
- **Cost per article** (~2,500 chars): **$0.075**

#### 2. Neural2 Voice
- **Price**: $20 per 1 million characters
- **Quality**: High quality, excellent prosody
- **Best For**:
  - Natural-sounding narration
  - Balanced quality/cost
- **Voice ID**: `ml-IN-Neural2-A`
- **Cost per article** (~2,500 chars): **$0.05**

#### 3. WaveNet Voice (Current Default)
- **Price**: $16 per 1 million characters
- **Quality**: Premium quality, widely available
- **Best For**:
  - High-quality audio production
  - Reliable, stable option
- **Voice ID**: `ml-IN-Wavenet-A`
- **Cost per article** (~2,500 chars): **$0.04**

### Standard Voice

#### 4. Standard Voice
- **Price**: $4 per 1 million characters
- **Quality**: Basic quality
- **Best For**:
  - Cost-effective solutions
  - Development/testing
- **Cost per article** (~2,500 chars): **$0.01**

---

## 📈 Cost Comparison Examples

### Per Article Costs (2,500 characters)

| Voice | Cost per Article | Monthly (100 articles) | Annual (1,200 articles) |
|-------|------------------|------------------------|-------------------------|
| Chirp | $0.075 | $7.50 | $90.00 |
| Neural2 | $0.05 | $5.00 | $60.00 |
| WaveNet | $0.04 | $4.00 | $48.00 |
| Standard | $0.01 | $1.00 | $12.00 |

### Monthly Costs (1,800 articles @ 2,500 chars each = 4.5M chars)

| Voice | Characters | After Free Tier | Cost |
|-------|------------|-----------------|------|
| Chirp | 4.5M | 500K | **$15.00** |
| Neural2 | 4.5M | 500K | **$10.00** |
| WaveNet | 4.5M | 500K | **$8.00** |
| Standard | 4.5M | 500K | **$2.00** |

**Note**: Google Cloud provides **4 million characters FREE per month** for all voice types.

### Monthly Costs (1,800 articles @ 2,700 chars each = 4.86M chars)

| Voice | Characters | After Free Tier | Cost |
|-------|------------|-----------------|------|
| Chirp | 4.86M | 860K | **$25.80** |
| Neural2 | 4.86M | 860K | **$17.20** |
| WaveNet | 4.86M | 860K | **$13.76** |
| Standard | 4.86M | 860K | **$3.44** |

---

## 💡 Cost Savings Comparison

### Chirp vs WaveNet
- **Chirp costs 87.5% more** than WaveNet
- **Savings with WaveNet**: $12.04/month (at 4.86M chars)
- **Annual savings**: $144.48

### Chirp vs Neural2
- **Chirp costs 50% more** than Neural2
- **Savings with Neural2**: $8.60/month (at 4.86M chars)
- **Annual savings**: $103.20

### Neural2 vs WaveNet
- **Neural2 costs 25% more** than WaveNet
- **Savings with WaveNet**: $3.44/month (at 4.86M chars)
- **Annual savings**: $41.28

---

## 🎯 Recommendations by Use Case

### For Maximum Quality (News Broadcasting)
**Recommended**: Chirp 3: HD
- **Cost**: $30/1M chars
- **Quality**: ⭐⭐⭐⭐⭐
- **Best when**: Quality is more important than cost

### For Balanced Quality/Cost
**Recommended**: Neural2
- **Cost**: $20/1M chars
- **Quality**: ⭐⭐⭐⭐
- **Best when**: You want high quality without premium pricing

### For Cost Optimization
**Recommended**: WaveNet
- **Cost**: $16/1M chars
- **Quality**: ⭐⭐⭐⭐
- **Best when**: You need premium quality at lower cost

### For Development/Testing
**Recommended**: Standard
- **Cost**: $4/1M chars
- **Quality**: ⭐⭐⭐
- **Best when**: Cost is the primary concern

---

## 📊 Free Tier Benefits

### Google Cloud TTS Free Tier
- **4 million characters per month**: **FREE** (all voice types)
- **Covers approximately**:
  - ~1,600 articles/month @ 2,500 chars each
  - ~1,481 articles/month @ 2,700 chars each

### Free Tier Coverage Examples

| Articles/Month | Characters | Chirp Cost | Neural2 Cost | WaveNet Cost |
|----------------|------------|------------|--------------|--------------|
| 1,000 | 2.5M | **FREE** | **FREE** | **FREE** |
| 1,500 | 3.75M | **FREE** | **FREE** | **FREE** |
| 1,800 | 4.5M | $15.00 | $10.00 | $8.00 |
| 2,000 | 5.0M | $30.00 | $20.00 | $16.00 |

---

## 🔄 Switching Between Voices

### Current Implementation
The system supports all three premium voices with automatic fallback:
1. **Chirp** (`voice_name='chirp'`)
2. **Neural2** (`voice_name='neural2'`)
3. **WaveNet** (`voice_name='wavenet'` or `'karthika'`) - Current default

### To Change Default Voice
Edit `backend/workers/tasks.py`:
```python
# Change from:
generate_audio_for_article(article, voice_name='wavenet')

# To:
generate_audio_for_article(article, voice_name='chirp')    # Best quality
# Or:
generate_audio_for_article(article, voice_name='neural2')   # Balanced
```

---

## 📋 Summary Table

| Metric | Chirp | Neural2 | WaveNet | Standard |
|--------|-------|---------|---------|----------|
| **Price/1M chars** | $30 | $20 | $16 | $4 |
| **Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Cost/Article** | $0.075 | $0.05 | $0.04 | $0.01 |
| **Monthly (1,800)** | $25.80 | $17.20 | $13.76 | $3.44 |
| **Annual (21,600)** | $309.60 | $206.40 | $165.12 | $41.28 |
| **Best For** | Premium | Balanced | Cost-effective | Testing |

---

## 🎯 Final Recommendation

**For Production News Site:**
- **Best Quality**: Chirp ($25.80/month for 1,800 articles)
- **Best Value**: WaveNet ($13.76/month for 1,800 articles)
- **Balanced**: Neural2 ($17.20/month for 1,800 articles)

**Current Default**: WaveNet (good balance of quality and cost)

---

## 📚 References

- [Google Cloud TTS Pricing](https://cloud.google.com/text-to-speech/pricing)
- Pricing as of 2024
- Prices may vary by region
- Free tier: 4M characters/month for all voice types

