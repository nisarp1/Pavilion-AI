# Cost Calculation - 60 Articles Per Day

## 📊 Overview

**Daily Production**: 60 articles  
**Monthly Production** (30 days): 1,800 articles  
**Annual Production** (365 days): 21,900 articles

---

## 📝 Assumptions

- **Average article length**: ~2,500 characters (after HTML tags and truncation)
- **Text generation**: Using Gemini Pro or Gemini 1.5 Pro
- **Voice generation**: Using Chirp, Neural2, WaveNet, or Standard voices
- **Daily articles**: 60 articles/day

---

## 1️⃣ Text Generation Costs (Gemini AI)

### Tokens per Article

| Component | Tokens |
|-----------|--------|
| Input (title, summary, URL, prompt) | ~500 tokens |
| Output (Malayalam + English content) | ~1,800 tokens |
| **Total per article** | **~2,300 tokens** |

### Daily Token Usage (60 articles)
- **Input Tokens**: 60 × 500 = **30,000 tokens/day**
- **Output Tokens**: 60 × 1,800 = **108,000 tokens/day**
- **Total Tokens**: **138,000 tokens/day**

### Monthly Token Usage (1,800 articles)
- **Input Tokens**: 1,800 × 500 = **900,000 tokens/month**
- **Output Tokens**: 1,800 × 1,800 = **3,240,000 tokens/month**
- **Total Tokens**: **4,140,000 tokens/month**

### Annual Token Usage (21,900 articles)
- **Input Tokens**: 21,900 × 500 = **10,950,000 tokens/year**
- **Output Tokens**: 21,900 × 1,800 = **39,420,000 tokens/year**
- **Total Tokens**: **50,370,000 tokens/year**

### Gemini Pricing (2024)

**Gemini 1.5 Pro:**
- Input: $1.25 per 1M tokens (first 1M free/month)
- Output: $5.00 per 1M tokens (first 1M free/month)

**Gemini Pro:**
- Input: $0.50 per 1M tokens (first 1M free/month)
- Output: $1.50 per 1M tokens (first 1M free/month)

### Cost Calculation - Gemini 1.5 Pro

#### Daily Costs (60 articles)
- **Input**: 30,000 tokens = FREE (within free tier)
- **Output**: 108,000 tokens = FREE (within free tier)
- **Daily Cost**: **$0.00**

#### Monthly Costs (1,800 articles)
- **Input**: (900,000 - 1,000,000 free) = 0 tokens × $1.25 = **$0**
- **Output**: (3,240,000 - 1,000,000 free) = 2,240,000 tokens × $5.00/1M = **$11.20**
- **Monthly Text Generation**: **$11.20**

#### Annual Costs (21,900 articles)
- **Input**: (10,950,000 - 12,000,000 free) = 0 tokens × $1.25 = **$0**
- **Output**: (39,420,000 - 12,000,000 free) = 27,420,000 tokens × $5.00/1M = **$137.10**
- **Annual Text Generation**: **$137.10**

### Cost Calculation - Gemini Pro (Cheaper)

#### Daily Costs (60 articles)
- **Input**: 30,000 tokens = FREE (within free tier)
- **Output**: 108,000 tokens = FREE (within free tier)
- **Daily Cost**: **$0.00**

#### Monthly Costs (1,800 articles)
- **Input**: (900,000 - 1,000,000 free) = 0 tokens × $0.50 = **$0**
- **Output**: (3,240,000 - 1,000,000 free) = 2,240,000 tokens × $1.50/1M = **$3.36**
- **Monthly Text Generation**: **$3.36**

#### Annual Costs (21,900 articles)
- **Input**: (10,950,000 - 12,000,000 free) = 0 tokens × $0.50 = **$0**
- **Output**: (27,420,000 - 12,000,000 free) = 15,420,000 tokens × $1.50/1M = **$23.13**
- **Annual Text Generation**: **$23.13**

---

## 2️⃣ Voice Generation Costs (Google Cloud TTS)

### Characters per Article
- Average article body: ~2,500 characters
- SSML overhead: ~200 characters
- **Total per article**: ~2,700 characters

### Daily Character Usage (60 articles)
- **Total Characters**: 60 × 2,700 = **162,000 characters/day**

### Monthly Character Usage (1,800 articles)
- **Total Characters**: 1,800 × 2,700 = **4,860,000 characters/month**

### Annual Character Usage (21,900 articles)
- **Total Characters**: 21,900 × 2,700 = **59,130,000 characters/year**

### Voice Pricing Comparison

| Voice | Price/1M Chars | Daily Cost | Monthly Cost | Annual Cost |
|-------|----------------|------------|--------------|-------------|
| **Chirp** | $30 | $4.86 | $25.80 | $309.60 |
| **Neural2** | $20 | $3.24 | $17.20 | $206.40 |
| **WaveNet** | $16 | $2.59 | $13.76 | $165.12 |
| **Standard** | $4 | $0.65 | $3.44 | $41.28 |

**Note**: Google Cloud provides **4 million characters FREE per month** for all voice types.

### Detailed Cost Breakdown

#### Chirp Voice ($30/1M chars)

**Daily (60 articles @ 162K chars):**
- Characters: 162,000
- Cost: **FREE** (within daily free tier equivalent)
- **Daily Cost**: **$0.00**

**Monthly (1,800 articles @ 4.86M chars):**
- Characters: 4,860,000
- After free tier: 4,860,000 - 4,000,000 = **860,000 characters**
- Cost: 860,000 / 1,000,000 × $30 = **$25.80**
- **Monthly Cost**: **$25.80**

**Annual (21,900 articles @ 59.13M chars):**
- Characters: 59,130,000
- After free tier: (59,130,000 - 48,000,000) = **11,130,000 characters**
- Cost: 11,130,000 / 1,000,000 × $30 = **$333.90**
- **Annual Cost**: **$333.90**

#### Neural2 Voice ($20/1M chars)

**Daily (60 articles @ 162K chars):**
- **Daily Cost**: **$0.00** (FREE)

**Monthly (1,800 articles @ 4.86M chars):**
- After free tier: 860,000 characters
- Cost: 860,000 / 1,000,000 × $20 = **$17.20**
- **Monthly Cost**: **$17.20**

**Annual (21,900 articles @ 59.13M chars):**
- After free tier: 11,130,000 characters
- Cost: 11,130,000 / 1,000,000 × $20 = **$222.60**
- **Annual Cost**: **$222.60**

#### WaveNet Voice ($16/1M chars)

**Daily (60 articles @ 162K chars):**
- **Daily Cost**: **$0.00** (FREE)

**Monthly (1,800 articles @ 4.86M chars):**
- After free tier: 860,000 characters
- Cost: 860,000 / 1,000,000 × $16 = **$13.76**
- **Monthly Cost**: **$13.76**

**Annual (21,900 articles @ 59.13M chars):**
- After free tier: 11,130,000 characters
- Cost: 11,130,000 / 1,000,000 × $16 = **$178.08**
- **Annual Cost**: **$178.08**

#### Standard Voice ($4/1M chars)

**Daily (60 articles @ 162K chars):**
- **Daily Cost**: **$0.00** (FREE)

**Monthly (1,800 articles @ 4.86M chars):**
- After free tier: 860,000 characters
- Cost: 860,000 / 1,000,000 × $4 = **$3.44**
- **Monthly Cost**: **$3.44**

**Annual (21,900 articles @ 59.13M chars):**
- After free tier: 11,130,000 characters
- Cost: 11,130,000 / 1,000,000 × $4 = **$44.52**
- **Annual Cost**: **$44.52**

---

## 3️⃣ Total Combined Costs

### Option 1: Gemini 1.5 Pro + Chirp (Best Quality)

| Period | Text Gen | Voice Gen | Total |
|--------|----------|-----------|-------|
| **Daily** (60 articles) | $0.00 | $0.00 | **$0.00** |
| **Monthly** (1,800 articles) | $11.20 | $25.80 | **$37.00** |
| **Annual** (21,900 articles) | $137.10 | $333.90 | **$471.00** |

### Option 2: Gemini Pro + Chirp (Balanced)

| Period | Text Gen | Voice Gen | Total |
|--------|----------|-----------|-------|
| **Daily** (60 articles) | $0.00 | $0.00 | **$0.00** |
| **Monthly** (1,800 articles) | $3.36 | $25.80 | **$29.16** |
| **Annual** (21,900 articles) | $23.13 | $333.90 | **$357.03** |

### Option 3: Gemini Pro + Neural2 (High Quality)

| Period | Text Gen | Voice Gen | Total |
|--------|----------|-----------|-------|
| **Daily** (60 articles) | $0.00 | $0.00 | **$0.00** |
| **Monthly** (1,800 articles) | $3.36 | $17.20 | **$20.56** |
| **Annual** (21,900 articles) | $23.13 | $222.60 | **$245.73** |

### Option 4: Gemini Pro + WaveNet (Cost Optimized)

| Period | Text Gen | Voice Gen | Total |
|--------|----------|-----------|-------|
| **Daily** (60 articles) | $0.00 | $0.00 | **$0.00** |
| **Monthly** (1,800 articles) | $3.36 | $13.76 | **$17.12** |
| **Annual** (21,900 articles) | $23.13 | $178.08 | **$201.21** |

### Option 5: Gemini Pro + Standard (Lowest Cost)

| Period | Text Gen | Voice Gen | Total |
|--------|----------|-----------|-------|
| **Daily** (60 articles) | $0.00 | $0.00 | **$0.00** |
| **Monthly** (1,800 articles) | $3.36 | $3.44 | **$6.80** |
| **Annual** (21,900 articles) | $23.13 | $44.52 | **$67.65** |

---

## 4️⃣ Cost Per Article Breakdown

### Option 1: Gemini 1.5 Pro + Chirp
- **Text**: $11.20 / 1,800 = **$0.0062 per article**
- **Voice**: $25.80 / 1,800 = **$0.0143 per article**
- **Total**: **$0.0205 per article**

### Option 2: Gemini Pro + Chirp
- **Text**: $3.36 / 1,800 = **$0.0019 per article**
- **Voice**: $25.80 / 1,800 = **$0.0143 per article**
- **Total**: **$0.0162 per article**

### Option 3: Gemini Pro + Neural2
- **Text**: $3.36 / 1,800 = **$0.0019 per article**
- **Voice**: $17.20 / 1,800 = **$0.0096 per article**
- **Total**: **$0.0115 per article**

### Option 4: Gemini Pro + WaveNet
- **Text**: $3.36 / 1,800 = **$0.0019 per article**
- **Voice**: $13.76 / 1,800 = **$0.0076 per article**
- **Total**: **$0.0095 per article**

### Option 5: Gemini Pro + Standard
- **Text**: $3.36 / 1,800 = **$0.0019 per article**
- **Voice**: $3.44 / 1,800 = **$0.0019 per article**
- **Total**: **$0.0038 per article**

---

## 5️⃣ Free Tier Coverage

### Gemini AI Free Tier
- **Input**: 1M tokens/month FREE
- **Output**: 1M tokens/month FREE
- **Covers**: ~435 articles/month (with current token usage)
- **Daily coverage**: ~14-15 articles/day FREE

### Google Cloud TTS Free Tier
- **Characters**: 4M characters/month FREE
- **Covers**: ~1,481 articles/month @ 2,700 chars each
- **Daily coverage**: ~49 articles/day FREE

### Combined Free Tier Analysis

**Daily (60 articles):**
- **Text**: 60 articles = **$0.00** (all within free tier)
- **Voice**: 60 articles = **$0.00** (all within free tier)
- **Total Daily**: **$0.00**

**Monthly (1,800 articles):**
- **Text**: 1,800 articles exceed free tier → **$3.36** (Gemini Pro)
- **Voice**: 1,800 articles exceed free tier → **$13.76-$25.80** (depending on voice)
- **Total Monthly**: **$17.12-$29.16**

---

## 6️⃣ Summary Table - 60 Articles Per Day

| Option | Text Model | Voice | Daily | Monthly | Annual | Cost/Article |
|--------|------------|-------|-------|---------|--------|--------------|
| **Best Quality** | Gemini 1.5 Pro | Chirp | $0.00 | **$37.00** | $471.00 | $0.0205 |
| **Balanced** | Gemini Pro | Chirp | $0.00 | **$29.16** | $357.03 | $0.0162 |
| **High Quality** | Gemini Pro | Neural2 | $0.00 | **$20.56** | $245.73 | $0.0115 |
| **Cost Optimized** | Gemini Pro | WaveNet | $0.00 | **$17.12** | $201.21 | $0.0095 |
| **Lowest Cost** | Gemini Pro | Standard | $0.00 | **$6.80** | $67.65 | $0.0038 |

---

## 7️⃣ Recommendations

### For 60 Articles Per Day:

**🥇 Best Quality (Recommended for News Site):**
- **Gemini Pro + Chirp**
- **Monthly Cost**: $29.16
- **Annual Cost**: $357.03
- **Quality**: ⭐⭐⭐⭐⭐

**🥈 Best Value:**
- **Gemini Pro + WaveNet**
- **Monthly Cost**: $17.12
- **Annual Cost**: $201.21
- **Quality**: ⭐⭐⭐⭐

**🥉 Cost Optimized:**
- **Gemini Pro + Standard**
- **Monthly Cost**: $6.80
- **Annual Cost**: $67.65
- **Quality**: ⭐⭐⭐

---

## 8️⃣ Cost Optimization Strategies

### Strategy 1: Reduce Article Length
- **Current**: 2,700 chars/article
- **Optimized**: 2,000 chars/article
- **Savings**: ~$5-8/month

### Strategy 2: Use Gemini Pro (Not 1.5 Pro)
- **Savings**: $7.84/month ($94.08/year)
- **Trade-off**: Slightly less advanced, but still excellent

### Strategy 3: Use WaveNet Instead of Chirp
- **Savings**: $12.04/month ($144.48/year)
- **Trade-off**: Slightly lower quality, but still premium

### Strategy 4: Combine Optimizations
- **Gemini Pro + WaveNet**: $17.12/month
- **Savings**: $19.88/month vs Best Quality option

---

## 9️⃣ Scaling Projections

### If Production Increases:

| Articles/Day | Monthly Articles | Monthly Cost (Gemini Pro + WaveNet) |
|--------------|------------------|-------------------------------------|
| 60 | 1,800 | $17.12 |
| 80 | 2,400 | $22.83 |
| 100 | 3,000 | $28.54 |
| 120 | 3,600 | $34.25 |

---

## 📋 Key Takeaways

✅ **Daily (60 articles)**: All costs covered by free tier = **$0.00/day**  
✅ **Monthly (1,800 articles)**: **$6.80-$37.00/month** depending on quality  
✅ **Annual (21,900 articles)**: **$67.65-$471.00/year** depending on quality  
✅ **Best Value**: Gemini Pro + WaveNet at **$17.12/month**  
✅ **Free tier covers**: ~49 articles/day for voice, ~14-15 articles/day for text  

---

**Last Updated**: 2024  
**Based on**: 60 articles per day production rate

