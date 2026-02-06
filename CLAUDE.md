# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Battery Scout is an automated battery industry newsletter platform. It scrapes global news, generates AI summaries via Google Gemini, and delivers personalized daily/weekly emails to subscribers.

**Stack:**
- Frontend: React 18 + TypeScript + Vite + TailwindCSS + shadcn/ui
- Backend: Python 3.11 + FastAPI + Supabase (PostgreSQL)
- Infrastructure: Railway (backend), Vercel (frontend), GitHub Actions (automation)

## Common Commands

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py                    # Runs API on http://localhost:8000

# Test scraping and email (standalone scripts)
python scrape_news.py
python send_email.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev                       # Runs on http://localhost:8080
npm run build                     # Production build to dist/
npm run lint                      # ESLint
npm test                          # Vitest (once)
npm run test:watch                # Vitest (watch mode)
```

## Architecture

### Data Flow
1. **GitHub Actions** (daily at 14:00 UTC) triggers `scrape_news.py` → fetches RSS, calls Gemini for summaries, stores in Supabase
2. **GitHub Actions** then triggers `send_email.py` → fetches subscribers, filters articles by preferences, sends via Gmail SMTP
3. **Frontend** handles signup/unsubscribe flows via FastAPI backend

### Backend Structure (`/backend`)
- `main.py` — FastAPI REST API with endpoints for signup, unsubscribe, topics, content, stats
- `scrape_news.py` — News scraping from Google News RSS across 8 languages, Gemini AI summarization
- `send_email.py` — Email delivery with personalization, deduplication, rate limiting
- `supabase_client.py` — All database operations encapsulated here
- `utils.py` — Token generation, validation, category mapping
- `email_template.py` — HTML and plain text email templates

### Frontend Structure (`/frontend/src`)
- `lib/api.ts` — Centralized API client (all backend calls go through here)
- `pages/` — Route pages (Index, Unsubscribe, NotFound)
- `components/` — SignupForm, HeroSection, ArticleCard, etc.
- `components/ui/` — shadcn/ui components

### Categories
```python
["Companies & Deals", "Policy & Regulation", "Supply Chain",
 "Lithium-ion & Solid-state", "Sodium-ion & Alternatives", "Recycling & Second-life"]
```

### Database Tables
- `subscribers` — email, frequency, categories[], regions[], pref_* boolean columns, is_active
- `articles` — title, url, summary, category, source_country, source_name, publish_date

## Key Patterns

### API Communication
Frontend uses `VITE_API_URL` env var to reach backend. Backend CORS allows localhost ports and Vercel/Netlify domains.

### Unsubscribe Tokens
SHA256 hash + base64 encoding using `UNSUBSCRIBE_SALT` env var. Generated in `utils.py`, verified on unsubscribe.

### Rate Limiting
- Gemini API: 6.5 second delay between calls, max 150 calls per scrape run
- Email sending: 1 second delay between emails

### Article Deduplication
`send_email.py` removes duplicates based on 70%+ word overlap in normalized titles.

## Environment Variables

### Backend Required
```
SUPABASE_URL, SUPABASE_SERVICE_KEY, GEMINI_API_KEY, GMAIL_USER, GMAIL_APP_PASSWORD, UNSUBSCRIBE_SALT
```

### Frontend Required
```
VITE_API_URL=http://localhost:8000 (or production backend URL)
```

## GitHub Actions

`.github/workflows/daily_email.yml` runs daily:
1. Scrapes articles with `scrape_news.py`
2. Sends emails with `send_email.py`

Requires secrets: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `GEMINI_API_KEY`, `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `UNSUBSCRIBE_SALT`
