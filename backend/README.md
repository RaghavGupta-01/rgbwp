# GB Wind Forecast Decision Portal - Backend Service

FastAPI service delivering decision-time forecast selection and quantitative error analytics for the day-ahead buying desk.

## Structure
- `app/`: FastAPI application, configuration, schemas, and pure domain services (`decision.py`, `metrics.py`).
- `data/`: Committed Parquet snapshot data (`actuals.parquet`, `forecasts.parquet`, `snapshot_meta.json`).
- `ingestion/`: Elexon BMRS API client (`FUELHH` and `WINDFOR`), cleaning pipelines, and snapshot generation.
- `tests/`: Automated unit and API integration tests.

## Local Startup
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive OpenAPI documentation is available at `/docs`.
