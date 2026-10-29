"""Application configuration settings."""

import os
from pathlib import Path
from typing import List


class Settings:
    """Configurable application settings."""

    # Domain scope defaults (Purchase decisions in Jan 2026 -> Delivery 2 Jan to 1 Feb)
    DECISION_DATE_FROM: str = "2026-01-01"
    DECISION_DATE_TO: str = "2026-01-31"
    DELIVERY_DATE_FROM: str = "2026-01-02"
    DELIVERY_DATE_TO: str = "2026-02-01"

    # Decision cutoff time (default 09:00 Europe/London)
    DEFAULT_CUTOFF_TIME: str = "09:00"
    DEFAULT_TIMEZONE: str = "Europe/London"

    # CORS configuration
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,*"
        ).split(",")
        if origin.strip()
    ]

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"


settings = Settings()
