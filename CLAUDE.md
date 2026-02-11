# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

Hungry Monkey is a restaurant discovery and recommendation application with voice integration. Users can find restaurants using AI-powered recommendations, Yelp API data, and phone-based voice interaction via VAPI. Features Clerk authentication and Supabase for data storage. Deployed on Vercel.

## Tech Stack

### Frontend
- **Language**: TypeScript
- **Framework**: React 18.3 + Vite
- **Styling**: Tailwind CSS
- **Auth**: Clerk
- **Linting**: ESLint

### Backend
- **Language**: Python 3.9+
- **Framework**: FastAPI 0.115.5
- **Database**: Supabase
- **AI**: Anthropic API (Claude)
- **Voice**: VAPI (phone number integration)
- **Restaurant Data**: Yelp Fusion API

### Deployment
- **Platform**: Vercel
- **Config**: `vercel.json`

## Project Structure

```
hungry-monkey/
├── package.json                 # Root -- concurrently runner for dev
├── frontend/
│   ├── package.json             # React + Vite dependencies
│   ├── vite.config.ts           # Vite configuration
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   └── App.tsx              # Root component
│   └── public/                  # Static assets
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── routes/                  # API route handlers
│   ├── services/                # Business logic
│   └── examples/
│       ├── test_api.py          # API test scripts
│       └── supabase_test.py     # Supabase connection test
├── requirements.txt             # Python dependencies
├── vercel.json                  # Vercel deployment config
├── .env.example                 # Environment variable template
└── .github/workflows/
    └── claude.yml               # Claude Code Actions workflow
```

## Development Commands

```bash
# Run both frontend and backend together
npm run dev

# Frontend only
npm run dev:frontend         # Vite dev server (http://localhost:5173)

# Backend only
npm run dev:backend          # FastAPI uvicorn (http://localhost:8000)

# Frontend build
cd frontend && npm run build

# Frontend lint
cd frontend && npm run lint

# Backend setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run backend directly
uvicorn app.main:app --reload --port 8000
```

## Environment & Config

### Required Environment Variables
```bash
# Supabase
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-supabase-anon-key>

# Clerk (frontend)
VITE_CLERK_PUBLISHABLE_KEY=<your-clerk-key>

# Yelp
YELP_API_KEY=<your-yelp-fusion-api-key>

# Anthropic
ANTHROPIC_API_KEY=<your-anthropic-key>

# VAPI (voice)
VAPI_API_KEY=<your-vapi-key>
```

- Root `.env` for backend variables
- `frontend/.env` for frontend variables (prefixed with `VITE_`)
- See `.env.example` for templates
- Never commit `.env` files

## Code Style & Standards

### Frontend
- TypeScript with React best practices
- ESLint for code quality
- Tailwind CSS utility classes
- Component-based architecture

### Backend
- Python type hints
- FastAPI dependency injection
- Async route handlers where appropriate
- Service layer pattern (routes -> services -> external APIs)

## Architecture Notes

- Frontend calls backend REST API for restaurant data and recommendations
- Backend aggregates data from Yelp API and processes with Anthropic Claude
- Supabase stores user preferences and history
- VAPI provides phone-based voice interaction for hands-free restaurant search
- Clerk handles authentication on the frontend
- Vercel deploys both frontend (static) and backend (serverless functions)

## Troubleshooting

- Frontend build errors: Delete `node_modules/` and `npm install` in both root and `frontend/`
- Backend import errors: Ensure venv is activated
- Yelp API errors: Check API key validity and rate limits
- Supabase connection issues: Verify SUPABASE_URL and SUPABASE_KEY
- VAPI not working: Ensure phone number is configured in VAPI dashboard
