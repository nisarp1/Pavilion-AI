# 🚀 Pavilion AI: Project Technical Documentation

Detailed overview of the Pavilion AI (PavilionEnd) project, its features, and technical architecture.

---

## 📖 Introduction
Pavilion AI is an automated, AI-driven news platform designed to scout, generate, and publish sports content (specifically Football and Cricket) for Malayalam-speaking audiences. It leverages state-of-the-art Generative AI to transform raw global news into localized editorial content and video.

---

## 🏗️ System Architecture

The project consists of three primary layers:

### 1. The Engine (Backend)
- **Technology:** Python with the **Django REST Framework**.
- **Role:** Handles the database, AI prompt engineering, and communication with external APIs (Google Gemini, NewsAPI, D-ID).
- **Automation:** Uses **Celery & Redis** to run tasks in the background (like video generation and trend fetching) without slowing down the website.

### 2. The Dashboard (Frontend)
- **Technology:** **React** with **Tailwind CSS**.
- **Role:** Providing an admin interface where editors can see incoming "Fetched" news, click "Generate" to create articles, and manage the publishing workflow (Draft → Published).

### 3. The Public Website (Consumer Theme)
- **Technology:** Custom **PHP** (WordPress-style structure).
- **Role:** Serving the final articles to the public with high performance and mobile-first design.

---

## 🌟 Core Features

### 🔍 Automated News Scouting
Integrated scouts monitor **RSS Feeds** and **Google Trends**.
- **Sources:** ESPN Cricket, BBC Football, Google News.
- **Frequency:** Checks every 5 minutes for new updates.
- **Filtering:** Automatically filters for relevance to the Indian and Malayalam-speaking audience.

### ✍️ AI-Powered Malayalam Writing
Instead of basic translation, the system uses **Google Gemini** to write professional editorial content.
- **Malayalam Editorial Style:** Uses journalistic vocabulary common in Kerala’s leading news portals.
- **SEO Optimization:** Automatically generates Meta Titles and Descriptions in Malayalam for Google search ranking.
- **English Context:** Keeps an English summary and slug (URL) for better SEO performance.

### 🎙️ AI Voice & Video Pipeline
Transforms text into a full multimedia experience.
- **Audio:** Uses **Google Cloud TTS (Text-to-Speech)** with high-quality Malayalam neural voices.
- **Video:** Uses **D-ID AI** to animate a virtual news anchor that \"speaks\" the article text.
- **Formats:** Supports Portrait (9:16) for TikTok/Reels and Landscape (16:9) for YouTube.

### 📊 Trend Monitoring
Uses **pytrends** to fetch real-time search volume from Google. Articles are "enriched" with search interest scores, helping editors prioritize content that is currently trending or "viral."

---

## 🛠️ Technical Stack Summary

| Tool | Purpose |
| :--- | :--- |
| **Python / Django** | Main backend logic and API service. |
| **React** | Interactive dashboard interface. |
| **Google Gemini** | Language logic and article generation. |
| **D-ID API** | AI Character Video generation. |
| **PostgreSQL** | Permanent data storage. |
| **Redis** | Temporary storage for background tasks. |
| **Vercel Blob** | High-speed storage for generated audio/video files. |

---

## 🚀 Future Roadmap
- **Vertex AI Integration:** Moving towards Google Cloud's enterprise AI platform.
- **Multi-tenant Support:** Allowing multiple news brands to use the same engine.
- **Advanced Social Post Generation:** Automatically creating Instagram/Facebook posts from articles.

---
*Created by Antigravity AI for Pavilion AI Project.*
