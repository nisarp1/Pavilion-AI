# Monthly Cost Calculation for 1,800 Published Articles

## Overview

This document calculates the estimated monthly costs for:
1. **Text Generation** (Gemini AI)
2. **Voice Generation** (Google Cloud TTS - Chirp)

## Assumptions

- **Articles per month**: 1,800 published articles
- **Average article length**: ~2,500 characters (after HTML tags and truncation)
- **Text generation**: Using Gemini Pro or Gemini 1.5 Pro
- **Voice generation**: Using Chirp 3: HD voice ($30/1M characters)

---

## 1. Text Generation Costs (Gemini AI)

### Input Tokens (per article)
- Title: ~10-15 tokens
- Summary: ~50-100 tokens  
- Source URL: ~20 tokens
- Prompt: ~400 tokens
- **Total Input**: ~500 tokens per article

### Output Tokens (per article)
- Malayalam title: ~15-20 tokens
- Malayalam summary: ~80-120 tokens
- English summary: ~80-120 tokens
- Malayalam body (4-5 paragraphs): ~1,500-2,000 tokens
- Meta tags: ~100 tokens
- **Total Output**: ~1,800 tokens per article

### Total Tokens per Article
- **Input**: 500 tokens
- **Output**: 1,800 tokens
- **Total**: 2,300 tokens per article

### Monthly Token Usage
- **Total Input Tokens**: 1,800 articles × 500 tokens = **900,000 tokens**
- **Total Output Tokens**: 1,800 articles × 1,800 tokens = **3,240,000 tokens**
- **Total Tokens**: 4,140,000 tokens

### Gemini Pricing (as of 2024)
**Gemini 1.5 Pro:**
- Input: $1.25 per 1M tokens (first 1M free/month)
- Output: $5.00 per 1M tokens (first 1M free/month)

**Gemini Pro:**
- Input: $0.50 per 1M tokens (first 1M free/month)
- Output: $1.50 per 1M tokens (first 1M free/month)

### Cost Calculation (Gemini 1.5 Pro)
- **Input Cost**: (900,000 - 1,000,000 free) = 0 tokens × $1.25 = **$0**
- **Output Cost**: (3,240,000 - 1,000,000 free) = 2,240,000 tokens × $5.00/1M = **$11.20**
- **Total Text Generation**: **$11.20/month**

### Cost Calculation (Gemini Pro - Cheaper Option)
- **Input Cost**: (900,000 - 1,000,000 free) = 0 tokens × $0.50 = **$0**
- **Output Cost**: (3,240,000 - 1,000,000 free) = 2,240,000 tokens × $1.50/1M = **$3.36**
- **Total Text Generation**: **$3.36/month**

---

## 2. Voice Generation Costs (Chirp TTS)

### Characters per Article
- Average article body: ~2,500 characters (after truncation to 4,000 chars)
- SSML overhead: ~200 characters
- **Total per article**: ~2,700 characters

### Monthly Character Usage
- **Total Characters**: 1,800 articles × 2,700 characters = **4,860,000 characters**

### Chirp Pricing
- **Price**: $30 per 1 million characters
- **Free Tier**: First 4 million characters/month FREE (for all voice types)

### Cost Calculation
- **Characters after free tier**: 4,860,000 - 4,000,000 = **860,000 characters**
- **Cost**: 860,000 / 1,000,000 × $30 = **$25.80**
- **Total Voice Generation**: **$25.80/month**

**Note**: If articles average 2,000 characters instead of 2,700:
- Total: 1,800 × 2,000 = 3,600,000 characters
- After free tier: 0 characters (all covered by free tier)
- **Cost**: **$0/month** (all within free tier!)

---

## 3. Total Monthly Costs

### Option 1: Gemini 1.5 Pro + Chirp (Best Quality)
- Text Generation: **$11.20/month**
- Voice Generation: **$25.80/month**
- **TOTAL**: **$37.00/month**

### Option 2: Gemini Pro + Chirp (Balanced)
- Text Generation: **$3.36/month**
- Voice Generation: **$25.80/month**
- **TOTAL**: **$29.16/month**

### Option 3: Gemini Pro + WaveNet (Cost Optimized)
- Text Generation: **$3.36/month**
- Voice Generation: (4,860,000 - 4,000,000) / 1M × $16 = **$13.76/month**
- **TOTAL**: **$17.12/month**

---

## 4. Cost Breakdown per Article

### Option 1 (Gemini 1.5 Pro + Chirp)
- Text: $11.20 / 1,800 = **$0.0062 per article**
- Voice: $25.80 / 1,800 = **$0.0143 per article**
- **Total**: **$0.0205 per article**

### Option 2 (Gemini Pro + Chirp)
- Text: $3.36 / 1,800 = **$0.0019 per article**
- Voice: $25.80 / 1,800 = **$0.0143 per article**
- **Total**: **$0.0162 per article**

### Option 3 (Gemini Pro + WaveNet)
- Text: $3.36 / 1,800 = **$0.0019 per article**
- Voice: $13.76 / 1,800 = **$0.0076 per article**
- **Total**: **$0.0095 per article**

---

## 5. Annual Costs

### Option 1 (Gemini 1.5 Pro + Chirp)
- **Monthly**: $37.00
- **Annual**: $444.00

### Option 2 (Gemini Pro + Chirp)
- **Monthly**: $29.16
- **Annual**: $349.92

### Option 3 (Gemini Pro + WaveNet)
- **Monthly**: $17.12
- **Annual**: $205.44

---

## 6. Cost Optimization Strategies

### Strategy 1: Use Gemini Pro (Not 1.5 Pro)
- **Savings**: $7.84/month ($94.08/year)
- **Trade-off**: Slightly less advanced model, but still excellent quality

### Strategy 2: Use WaveNet Instead of Chirp
- **Savings**: $12.04/month ($144.48/year)
- **Trade-off**: Slightly lower voice quality, but still premium

### Strategy 3: Combine Both Optimizations
- **Savings**: $19.88/month ($238.56/year)
- **Total Cost**: $17.12/month

### Strategy 4: Monitor and Optimize Article Length
- Reduce average article length from 2,500 to 2,000 characters
- **Savings**: ~$5-8/month

---

## 7. Free Tier Benefits

### Gemini AI Free Tier
- **Input**: 1M tokens/month FREE
- **Output**: 1M tokens/month FREE
- **Covers**: ~435 articles/month (with current token usage)

### Google Cloud TTS Free Tier
- **Characters**: 4M characters/month FREE
- **Covers**: ~1,481 articles/month (with current character usage)

### Combined Free Tier Coverage
- **Text**: ~435 articles/month FREE
- **Voice**: ~1,481 articles/month FREE
- **Bottleneck**: Text generation (Gemini free tier)

---

## 8. Scaling Projections

### 2,000 Articles/Month
- **Gemini Pro + Chirp**: ~$32.50/month
- **Gemini Pro + WaveNet**: ~$19.00/month

### 3,000 Articles/Month
- **Gemini Pro + Chirp**: ~$48.75/month
- **Gemini Pro + WaveNet**: ~$28.50/month

### 5,000 Articles/Month
- **Gemini Pro + Chirp**: ~$81.25/month
- **Gemini Pro + WaveNet**: ~$47.50/month

---

## 9. Recommendations

### For 1,800 Articles/Month:

**Best Quality (Recommended)**:
- Gemini 1.5 Pro + Chirp
- **Cost**: $37.00/month
- **Quality**: ⭐⭐⭐⭐⭐

**Balanced (Good Value)**:
- Gemini Pro + Chirp
- **Cost**: $29.16/month
- **Quality**: ⭐⭐⭐⭐

**Cost Optimized**:
- Gemini Pro + WaveNet
- **Cost**: $17.12/month
- **Quality**: ⭐⭐⭐⭐

---

## 10. Notes

- Prices are estimates based on current Google Cloud pricing (2024)
- Actual costs may vary based on:
  - Article length variations
  - Token usage efficiency
  - Regional pricing differences
  - Promotional credits
- Free tiers reset monthly
- Monitor usage in Google Cloud Console
- Set up billing alerts to avoid surprises

---

## Summary

**For 1,800 published articles/month:**

| Option | Text Gen | Voice Gen | Total/Month | Total/Year |
|--------|----------|-----------|-------------|------------|
| **Best Quality** | $11.20 | $25.80 | **$37.00** | **$444** |
| **Balanced** | $3.36 | $25.80 | **$29.16** | **$350** |
| **Cost Optimized** | $3.36 | $13.76 | **$17.12** | **$205** |

**Recommendation**: Use **Gemini Pro + Chirp** for best balance of quality and cost at **$29.16/month**.

