# GB Wind Forecast Decision Portal

A web application designed for a UK energy utility's day-ahead power buying team to optimize procurement decisions under wind forecast uncertainty.

---

## 1. Overview & Purpose

The day-ahead trading team purchases power on day **D-1** for delivery across day **D**. Because wind generation is weather-dependent and variable, accurate day-ahead purchasing requires:
1. **Decision-Time Forecast Visibility**: Clearly presenting the latest wind generation forecast published prior to the daily decision cutoff time.
2. **Quantitative Accuracy Evaluation**: Evaluating historical forecast error against outturn actuals to establish empirical error buffers and procurement risk bounds.

### Time & Data Scope
- **Decision Window**: Purchase decisions made between **2026-01-01 and 2026-01-31** (D-1).
- **Delivery Days**: Electricity delivery dates from **2026-01-02 to 2026-02-01** (D).

- **Data Source**: Exclusively national-level GB wind from Elexon BMRS:
  - Half-hourly actual wind generation (`FUELHH` stream, `fuelType=WIND`).
  - Hourly wind generation forecasts (`WINDFOR` stream).

---

## 2. Repository Layout

```
.
├── README.md              # Project overview, quickstart, assumptions, and AI disclosure
├── docker-compose.yml     # One-command containerized local startup
├── .github/workflows/     # CI pipeline (lint, test, build)
├── backend/               # FastAPI service, domain calculations, ingestion pipeline, tests
├── frontend/              # Vite + React 18 + TypeScript web client
└── docs/                  # Architecture notes, system diagrams, and data findings
```

---

## 3. AI Assistance Disclosure

As required by the project specification, AI-assisted development tools were utilized during the development of this codebase to accelerate scaffolding, documentation, and test implementation. All domain logic, calculations, and architectural choices have been rigorously validated against project requirements.
