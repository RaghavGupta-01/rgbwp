# GB Wind Forecast Decision Portal

A day-ahead wind forecast decision portal for the GB power buying desk, visualizing decision-time forecasts and evaluating historical accuracy against actual outturn.

---

## Deployed Application
- **Live Web Portal**: [https://rgbwp.vercel.app](https://rgbwp.vercel.app/)
- **API Health Check**: [https://rgbwp.vercel.app/api/health](https://rgbwp.vercel.app/api/health)

---

## Files and Directories Overview

```
wind-forecast-portal/
├── docker-compose.yml          # One-command containerized local orchestration
├── .github/workflows/ci.yml    # GitHub Actions CI workflow (lint, test, build)
├── docs/
│   └── architecture.md         # System architecture, empirical data findings, and methodology
├── backend/
│   ├── Dockerfile              # Production Python 3.12-slim container
│   ├── pyproject.toml          # FastAPI dependencies, ruff, and pytest configuration
│   ├── app/
│   │   ├── main.py             # FastAPI entrypoint with CORS middleware
│   │   ├── config.py           # Configurable date ranges, cutoff defaults, and paths
│   │   ├── schemas.py          # Pydantic v2 response schemas
│   │   ├── api/routes.py       # REST API endpoints for metadata, forecasts, and metrics
│   │   ├── services/           # In-memory data store, decision logic, and error metrics
│   │   └── core/time_utils.py  # London/UTC timezone conversions and cutoff logic
│   ├── data/                   # Committed Parquet snapshots (actuals.parquet, forecasts.parquet)
│   ├── ingestion/              # Elexon BMRS client, cleaning, and snapshot generation CLI
│   └── tests/                  # Unit and integration test suite (domain, ingestion, API)
└── frontend/
    ├── Dockerfile              # Multi-stage container with inlined Nginx SPA proxy
    ├── package.json            # React, TypeScript, TanStack Query, ECharts, Tailwind CSS
    └── src/
        ├── App.tsx             # Root component and navigation state
        ├── api/                # Typed REST client and React Query hooks
        ├── components/         # Layout, ControlsBar, KpiCard, and ECharts visualizations
        └── pages/              # DecisionView ("Tomorrow's View") and AccuracyView
```

---

## How to Start the Application

### Option 1: With Docker (Recommended)
From the repository root:
```bash
docker compose up --build
```
- **Web Portal**: `http://localhost:5173` (or `http://localhost:3000`)
- **API & Docs**: `http://localhost:8000/docs`

*(Runs fully offline using the committed Parquet snapshot; no external database or API key required).*

### Option 2: Without Docker

#### 1. Backend (Python 3.10+)
```bash
cd backend
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -e ".[dev]"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API runs on `http://127.0.0.1:8000`.

#### 2. Frontend (Node.js 20+)
```bash
cd frontend
npm ci
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## AI Assistance Disclosure
AI-assisted tools were utilized during development for project scaffolding, architectural validation, and test automation. All domain logic, calculations, and code were manually verified against Elexon BMRS specifications.
