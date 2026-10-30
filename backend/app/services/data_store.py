"""In-memory data store for loading and caching Parquet snapshots."""

from pathlib import Path

import pandas as pd

from app.config import settings


class DataStore:
    """Manages in-memory Parquet snapshots of actuals and forecasts."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or settings.DATA_DIR
        self._actuals: pd.DataFrame | None = None
        self._forecasts: pd.DataFrame | None = None

    def load(self) -> None:
        """Load parquet datasets into memory."""
        actuals_path = self.data_dir / "actuals.parquet"
        forecasts_path = self.data_dir / "forecasts.parquet"

        if not actuals_path.exists() or not forecasts_path.exists():
            raise FileNotFoundError(
                f"Parquet snapshot files not found in {self.data_dir}."
            )

        self._actuals = pd.read_parquet(actuals_path)
        self._forecasts = pd.read_parquet(forecasts_path)

        # Ensure datetime types
        self._actuals["start_time"] = pd.to_datetime(
            self._actuals["start_time"], utc=True
        )
        self._forecasts["publish_time"] = pd.to_datetime(
            self._forecasts["publish_time"], utc=True
        )
        self._forecasts["start_time"] = pd.to_datetime(
            self._forecasts["start_time"], utc=True
        )

    @property
    def actuals(self) -> pd.DataFrame:
        if self._actuals is None:
            self.load()
        return self._actuals

    @property
    def forecasts(self) -> pd.DataFrame:
        if self._forecasts is None:
            self.load()
        return self._forecasts


# Global singleton instance
data_store = DataStore()
