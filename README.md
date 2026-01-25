# Battery Scout

**Automated battery industry newsletter service** — curates news from global sources, generates AI summaries, and delivers personalized daily/weekly emails.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8-blue.svg)](https://www.typescriptlang.org/)

## 📋 Overview

Battery Scout is a full-stack newsletter platform that:
- **Scrapes** battery industry news from Google News across 8+ languages
- **Summarizes** articles using Google Gemini AI
- **Categorizes** content into 6 industry-relevant topics
- **Personalizes** newsletters based on subscriber preferences
- **Delivers** daily/weekly emails via automated GitHub Actions

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │  ← User signup/unsubscribe
│   (Vite + TS)   │
└────────┬────────┘
         │ REST API
         ↓
┌─────────────────┐
│  FastAPI Backend│  ← Subscription management
│   (Python 3.11) │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│    Supabase     │  ← Database (subscribers, articles)
│   (PostgreSQL)  │
└─────────────────┘

GitHub Actions (daily cron)
  ↓
  1. scrape_news.py   → Fetch & summarize articles
  2. send_email.py    → Send personalized emails
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Supabase account** (for database)
- **Google Gemini API key** (for AI summaries)
- **Gmail account** (for sending emails)

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
export SUPABASE_URL=your_supabase_url
export SUPABASE_SERVICE_KEY=your_service_key
export GEMINI_API_KEY=your_gemini_key
export GMAIL_USER=your_email@gmail.com
export GMAIL_APP_PASSWORD=your_app_password
export UNSUBSCRIBE_SALT=random_secret_string

# Run the API server
python main.py
# Server runs on http://localhost:8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables (create .env file)
echo "VITE_API_URL=http://localhost:8000" > .env

# Start dev server
npm run dev
# App runs on http://localhost:8080
```

## 📂 Project Structure

```
Battery Scout/
├── backend/
│   ├── main.py              # FastAPI server & API endpoints
│   ├── scrape_news.py       # News scraping & AI summarization
│   ├── send_email.py        # Email delivery service
│   ├── supabase_client.py   # Database operations
│   ├── utils.py             # Validation & helpers
│   ├── email_template.py    # HTML email templates
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Route pages
│   │   ├── lib/
│   │   │   └── api.ts       # Backend API client
│   │   └── integrations/    # Supabase client (legacy)
│   ├── package.json
│   └── vite.config.ts
│
├── .github/
│   └── workflows/
│       └── daily_email.yml  # Automated daily newsletter
│
└── README.md
```

## 🔧 Configuration

### Backend Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Your Supabase project URL | ✅ |
| `SUPABASE_SERVICE_KEY` | Supabase service role key | ✅ |
| `GEMINI_API_KEY` | Google Gemini API key | ✅ |
| `GMAIL_USER` | Gmail address for sending | ✅ |
| `GMAIL_APP_PASSWORD` | Gmail app password | ✅ |
| `UNSUBSCRIBE_SALT` | Secret for token generation | ✅ |
| `FRONTEND_URL` | Production frontend URL | Optional |
| `PORT` | Server port (default: 8000) | Optional |

### Frontend Environment Variables

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API URL (e.g., `http://localhost:8000`) |

## 📡 API Endpoints

### Public Endpoints

- `GET /` — Health check
- `GET /api/topics` — Get available categories
- `GET /api/content` — Get sample articles
- `GET /api/stats` — Get subscriber statistics
- `POST /api/signup` — Subscribe to newsletter
- `POST /api/unsubscribe/verify` — Verify unsubscribe token
- `POST /api/unsubscribe/confirm` — Confirm unsubscribe

See full API docs at `http://localhost:8000/docs` (Swagger UI)

## 🤖 Automation

The newsletter runs automatically via **GitHub Actions**:

1. **Daily at 14:00 UTC** (9am EST / 6am PST)
2. Scrapes news from past 24 hours
3. Generates AI summaries
4. Sends personalized emails

Manual trigger: Go to **Actions** tab → **Daily Newsletter** → **Run workflow**

## 📧 Categories

1. **Companies & Deals** — Partnerships, acquisitions, factory openings
2. **Policy & Regulation** — Tariffs, subsidies, government regulations
3. **Supply Chain** — Lithium, cobalt, nickel mining and pricing
4. **Lithium-ion & Solid-state** — Battery tech breakthroughs
5. **Sodium-ion & Alternatives** — Next-gen battery chemistries
6. **Recycling & Second-life** — Circular economy, reuse, recycling

## 🌍 Regional Coverage

- **North America** (US, Canada)
- **Europe** (Germany, France, UK, Sweden, etc.)
- **Asia** (China, Japan, South Korea, India)
- **Global** (all regions)

News is scraped in 8 languages: English, Chinese, German, Japanese, Korean, Hungarian, Swedish, French, Spanish

## 🚢 Deployment

### Backend (Railway/Render/Fly.io)

```bash
# Set all environment variables in your platform
# Deploy from backend/ directory
```

### Frontend (Vercel/Netlify)

```bash
# Set VITE_API_URL to your backend URL
# Deploy from frontend/ directory
vercel --prod
```

### Database (Supabase)

Run the migration in `frontend/supabase/migrations/` to set up tables.

## 🧪 Testing

```bash
# Frontend tests
cd frontend
npm test

# Backend (manual testing)
cd backend
python scrape_news.py  # Test scraping
python send_email.py   # Test email sending
```

## 📝 Development Workflow

1. **Backend changes**: Edit Python files, restart server
2. **Frontend changes**: Hot reload via Vite
3. **Database schema**: Update Supabase migrations
4. **New categories**: Update `NEW_CATEGORIES` in `supabase_client.py`

## 🔒 Security Notes

- Never commit `.env` files
- Use service role key for backend (not anon key)
- Rotate `UNSUBSCRIBE_SALT` if exposed
- Use Gmail app passwords (not account password)

## 🐛 Troubleshooting

**Frontend can't reach backend**
- Check `VITE_API_URL` is set correctly
- Verify backend CORS allows frontend domain

**No articles scraped**
- Check Gemini API quota/limits
- Verify Google News RSS is accessible

**Emails not sending**
- Verify Gmail app password is correct
- Check Gmail "Less secure app access" settings

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

This is a personal project, but suggestions are welcome! Open an issue to discuss changes.

## 📧 Contact

For questions about the newsletter: [Your Contact Info]

---

**Built with** ❤️ **for battery industry professionals**
