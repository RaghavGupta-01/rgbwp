# Architecture & System Design

This document outlines the architecture, data pipeline, and empirical findings for the GB Wind Forecast Decision Portal.

---

## 1. System Architecture

```
Elexon BMRS API (FUELHH, WINDFOR)
        │
        ▼ (ingestion pipeline with retry and chunking)
backend/data/*.parquet (Snapshot + snapshot_meta.json)
        │
        ▼ (loaded into memory at startup)
FastAPI Backend (FastAPI, Pydantic v2, pandas, pyarrow)
  ├── services/decision.py (Pure function: latest forecast <= cutoff)
  ├── services/metrics.py (MAE, RMSE, Bias, P10-P95, breakdowns)
  └── core/time_utils.py (Timezone handling: Europe/London <-> UTC)
        │
        ▼ (REST /api endpoints with OpenAPI docs at /docs)
Vite + React 18 + TypeScript SPA
  ├── Page 1: Decision View (forecast curve, empirical error band, actuals, revisions)
  └── Page 2: Forecast Accuracy (KPIs, time series, horizon decay, error distributions)
```

### Architectural Decisions
1. **Committed Offline Snapshot**:
   - Zero network latency or external API downtime risk during operations.
   - January 2026 represents a fixed historical evaluation period; committing Parquet snapshots ensures full reproducibility.
2. **In-Memory Analytics**:
   - Total dataset size is compact (~1,500 actuals, tens of thousands of forecast rows).
   - Fast, deterministic in-memory operations in Python without needing a database server.
3. **Pure Function Domain Logic**:
   - Forecast selection and metric calculations are decoupled from the web framework and covered by automated unit tests.

---

## 2. Elexon BMRS Data Findings

Empirical inspection of the Elexon BMRS `WINDFOR` forecast stream revealed several critical characteristics:

1. **Publish Cadence**:
   - Forecasts are published approximately 8 times per day (every 2–4 hours; typical median interval is ~3 hours).
2. **Forecast Horizons & Historical Back-Casts**:
   - Each forecast batch publishes 73 hourly steps extending up to ~66.5 hours ahead.
   - Crucially, ~20.5% of rows in each publication have `horizon_h <= 0` (start times earlier than publication time).
   - **Requirement**: These negative horizon rows must be strictly dropped during ingestion cleaning.
3. **Version Density**:
   - Each target delivery hour contains between 8 and 24 forecast versions (median 16), providing ample history for revision tracking.
4. **Generation Range**:
   - Observed national wind generation spans ~5,000 MW to ~20,500 MW, with no negative or missing generation values.

---

## 3. Domain Logic & Calculations

1. **Decision Cutoff**:
   - Decisions for delivery day **D** are evaluated at day-ahead cutoff time `D-1 at 09:00 Europe/London` (equal to UTC in January).
2. **Hourly Grid Alignment**:
   - Forecasts are hourly. Half-hourly actuals (`FUELHH`) are averaged pairwise into hourly actuals to match the forecast grid.
3. **Error Convention**:
   - `error = forecast - actual` (MW). Positive values represent over-forecasting; negative values represent under-forecasting.
