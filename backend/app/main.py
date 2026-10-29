"""FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(
    title="GB Wind Forecast Decision Portal API",
    description=(
        "REST API providing decision-time GB wind forecasts "
        "and forecast accuracy metrics."
    ),
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["System"])
def health_check() -> dict:
    """Service liveness probe."""
    return {"status": "ok"}
