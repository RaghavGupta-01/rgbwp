# System Architecture & Design

This document details the architecture, data pipeline, and analytical methodology for the GB Wind Forecast Decision Portal.

---

## 1. System Architecture

```
┌────────────────────────────────────────────────────────┐
│              Elexon BMRS API (v1)                     │
│  - FUELHH Stream (Half-Hourly Actuals, fuelType=WIND)  │
│  - WINDFOR Stream (Hourly Wind Generation Forecasts)   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           │ Ingestion Pipeline (build_snapshot.py)
                           │ • Chunked HTTP requests with retries
                           │ • UTC timestamp normalization
                           │ • Negative horizon filtering (drop horizon <= 0)
                           ▼
┌────────────────────────────────────────────────────────┐
│             Parquet Snapshot Storage                   │
│  - backend/data/actuals.parquet                        │
│  - backend/data/forecasts.parquet                      │
│  - backend/data/snapshot_meta.json                     │
└──────────────────────────┬─────────────────────────────┘
                           │
                           │ In-Memory Loading at Startup (DataStore)
                           ▼
┌────────────────────────────────────────────────────────┐
│                FastAPI Backend Service                 │
│  - services/decision.py: Decision-time forecast filter │
│  - services/metrics.py: MAE, RMSE, Bias, Percentiles   │
│  - core/time_utils.py: Europe/London and UTC handling  │
│  - api/routes.py: Typed REST Endpoints                 │
└──────────────────────────┬─────────────────────────────┘
                           │
                           │ JSON REST API (TanStack Query)
                           ▼
┌────────────────────────────────────────────────────────┐
│          Vite + React + TypeScript Web App             │
│  - Decision View ("Tomorrow's View")                   │
│    • Key metrics (Peak, Average, Baseload, Lead Time)  │
│    • Decision Curve with Empirical Uncertainty Band    │
│    • Actuals Overlay (Half-Hourly)                     │
│    • Forecast Revisions Evolution Chart                │
│  - Forecast Accuracy View                              │
│    • Accuracy KPIs (MAE, RMSE, Bias, P90, nMAE)        │
│    • Procurement buffer sizing guidance                │
│    • Daily error time series                           │
│    • Hour-of-day error & bias profiles                 │
│    • Lead-time decay curves                            │
│    • Error distribution histogram                      │
│    • Error breakdown by generation level               │
└────────────────────────────────────────────────────────┘
```

---

## 2. Design Decisions & Rationale

### 2.1 Snapshot Storage vs. Live API Calls
- **Strategy**: Historical evaluation data is fetched, validated, and stored as local Parquet snapshots. A standalone CLI script (`build_snapshot.py`) allows re-fetching and updating data on demand.
- **Benefits**:
  - Eliminates external API availability dependencies during trading decisions.
  - Ensures deterministic, reproducible analysis.
  - Near-instantaneous API response times (<10ms).

### 2.2 In-Memory Analytics vs. Database Server
- **Strategy**: Parquet files are loaded into an in-memory `DataStore` singleton at application startup. All filtering, aggregation, and error calculations execute via optimized vector operations.
- **Benefits**:
  - Eliminates database connection management and external infrastructure overhead.
  - Simplifies local development and container deployments.

### 2.3 Decoupled Domain Services
- **Strategy**: Decision logic and error calculations are implemented as pure functions in `services/decision.py` and `services/metrics.py`, decoupled from web framework controllers.
- **Benefits**:
  - Independent unit testing with synthetic edge cases.
  - Clear separation of business logic from HTTP routing.

---

## 3. Data Pipeline & Observations

Inspection of the Elexon BMRS data feeds established key ingestion requirements:

| Dimension | Observed Characteristic | Ingestion Handling |
| :--- | :--- | :--- |
| **Publish Cadence** | Forecast batches are published roughly every 2 to 4 hours. | Provides multiple version vintages per delivery hour for revision tracking. |
| **Forecast Horizon** | Publications contain forward projections up to ~66.5 hours ahead. | Sufficient forward coverage for day-ahead decision cutoffs. |
| **Back-casts** | A portion of published records contain start times earlier than publish time. | Explicitly discarded during ingestion; only records with forward horizons are retained. |
| **Granularity** | Forecasts are hourly; actuals are half-hourly. | Half-hourly actuals are averaged pairwise into hourly actuals for metric calculations, and retained as half-hourly for charting. |

---

## 4. Domain Calculations & Formulas

### 4.1 Decision-Time Forecast Selection
For delivery day $D$, the decision cutoff timestamp is computed in UTC:
$$\text{cutoff\_ts} = \text{to\_utc}(D - 1 \text{ at } \text{cutoff\_time} \text{ in Europe/London})$$

For each delivery hour $t \in [00:00, 23:00]$:
1. Filter candidate forecasts:
   $$\mathcal{F}_t = \{f \in \text{forecasts} \mid f.\text{start\_time} = t \land f.\text{publish\_time} \le \text{cutoff\_ts}\}$$
2. Select the latest version published before cutoff:
   $$f^*_t = \arg\max_{f \in \mathcal{F}_t} (f.\text{publish\_time})$$
3. If no forecast was published before cutoff, the hour is flagged as missing.

### 4.2 Error Metrics & Conventions
On the aligned hourly grid, forecast error is defined as:
$$e_t = \hat{y}_t - y_t \quad (\text{MW})$$
where $\hat{y}_t$ is the decision-time forecast and $y_t$ is the hourly actual wind generation.

- **Mean Absolute Error (MAE)**:
  $$\text{MAE} = \frac{1}{N} \sum_{t=1}^N |e_t|$$
- **Root Mean Squared Error (RMSE)**:
  $$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{t=1}^N e_t^2}$$
- **Mean Error / Bias**:
  $$\text{Bias} = \frac{1}{N} \sum_{t=1}^N e_t$$
  - $\text{Bias} > 0$: Over-forecast (buyer under-procured).
  - $\text{Bias} < 0$: Under-forecast (actual exceeded forecast).
- **Normalized MAE (nMAE)**:
  $$\text{nMAE} = \frac{\text{MAE}}{\bar{y}} \times 100\% \quad \text{where } \bar{y} = \frac{1}{N} \sum y_t$$
- **Empirical Uncertainty Band**:
  $$\text{Lower Band} = \hat{y}_t + P_{10}(e), \quad \text{Upper Band} = \hat{y}_t + P_{90}(e)$$
  where $P_{10}(e)$ and $P_{90}(e)$ are empirical percentiles of signed error over the evaluation period.

---

## 5. Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend** | FastAPI, Pydantic v2 | High-performance API with typed request/response schemas |
| **Data Engine** | pandas, pyarrow | In-memory data store, aggregations, and Parquet storage |
| **Ingestion** | httpx, tenacity | Resilient HTTP client with retry logic |
| **Frontend** | React, TypeScript, Vite | Single-page application with type safety |
| **State Management** | TanStack Query | Query caching, refetching, and API state handling |
| **Visualizations** | Apache ECharts | Interactive charting for curves, distributions, and decay profiles |
| **Styling** | Tailwind CSS | Clean, responsive design tokens |
| **DevOps** | Docker, Docker Compose | Containerized execution for local and production deployment |

---

## 6. Assumptions & Disclosures

- **Scope**: Purchase decisions evaluated across January 2026 ($D-1$), with delivery days spanning January 2 to February 1, 2026. (Configurable in `backend/app/config.py`).
- **Cutoff Default**: 09:00 Europe/London (equal to UTC in January). Conservative pre-gate closure default; configurable via UI and API.
- **Data Source**: Exclusively national-level GB wind generation from Elexon BMRS (`FUELHH` for actuals, `WINDFOR` for forecasts).
- **AI Assistance**: AI tools were used during development to assist with scaffolding, documentation structure, and test coverage. All domain calculations and architecture were manually verified.
