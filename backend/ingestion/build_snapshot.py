"""Build offline Parquet snapshot from Elexon BMRS API."""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

backend_root = Path(__file__).resolve().parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from ingestion.cleaning import clean_actuals, clean_forecasts  # noqa: E402
from ingestion.elexon_client import ElexonClient  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Scope dates per specification
# Purchase decisions in Jan 2026 -> Delivery 2026-01-02 to 2026-02-01
DELIVERY_DATE_FROM = "2026-01-02"
DELIVERY_DATE_TO = "2026-02-01"

# Pull forecasts starting 2 days prior so early Jan delivery days
# have decision-time forecasts available
FORECAST_PUBLISH_FROM = "2025-12-30T00:00:00Z"
FORECAST_PUBLISH_TO = "2026-02-01T23:59:59Z"


def build_snapshot(
    output_dir: Path | None = None,
    client: ElexonClient | None = None,
) -> None:
    """Execute ingestion pipeline, clean data, and write Parquet snapshots."""
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent.parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    if client is None:
        client = ElexonClient()

    logger.info(
        "Fetching FUELHH actuals from %s to %s...",
        DELIVERY_DATE_FROM,
        DELIVERY_DATE_TO,
    )
    raw_actuals = client.fetch_actuals_fuelhh(
        date_from=DELIVERY_DATE_FROM,
        date_to=DELIVERY_DATE_TO,
        chunk_days=7,
    )
    logger.info("Raw actuals fetched: %d rows", len(raw_actuals))
    df_actuals = clean_actuals(raw_actuals)
    logger.info("Cleaned actuals: %d rows", len(df_actuals))

    logger.info(
        "Fetching WINDFOR forecasts from %s to %s...",
        FORECAST_PUBLISH_FROM,
        FORECAST_PUBLISH_TO,
    )
    raw_forecasts = client.fetch_forecasts_windfor(
        publish_from=FORECAST_PUBLISH_FROM,
        publish_to=FORECAST_PUBLISH_TO,
        chunk_days=2,
    )
    logger.info("Raw forecasts fetched: %d rows", len(raw_forecasts))
    df_forecasts = clean_forecasts(raw_forecasts)
    logger.info("Cleaned forecasts: %d rows", len(df_forecasts))

    actuals_path = output_dir / "actuals.parquet"
    forecasts_path = output_dir / "forecasts.parquet"
    meta_path = output_dir / "snapshot_meta.json"

    logger.info("Writing actuals to %s...", actuals_path)
    df_actuals.to_parquet(actuals_path, index=False)

    logger.info("Writing forecasts to %s...", forecasts_path)
    df_forecasts.to_parquet(forecasts_path, index=False)

    snapshot_metadata = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "Elexon BMRS API v1",
        "endpoints": [
            "/datasets/FUELHH/stream",
            "/datasets/WINDFOR/stream",
        ],
        "actuals": {
            "file": "actuals.parquet",
            "row_count": len(df_actuals),
            "min_start_time": (
                df_actuals["start_time"].min().isoformat()
                if not df_actuals.empty
                else None
            ),
            "max_start_time": (
                df_actuals["start_time"].max().isoformat()
                if not df_actuals.empty
                else None
            ),
        },
        "forecasts": {
            "file": "forecasts.parquet",
            "row_count": len(df_forecasts),
            "min_publish_time": (
                df_forecasts["publish_time"].min().isoformat()
                if not df_forecasts.empty
                else None
            ),
            "max_publish_time": (
                df_forecasts["publish_time"].max().isoformat()
                if not df_forecasts.empty
                else None
            ),
            "min_start_time": (
                df_forecasts["start_time"].min().isoformat()
                if not df_forecasts.empty
                else None
            ),
            "max_start_time": (
                df_forecasts["start_time"].max().isoformat()
                if not df_forecasts.empty
                else None
            ),
        },
    }

    logger.info("Writing metadata to %s...", meta_path)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(snapshot_metadata, f, indent=2)

    logger.info("Snapshot build complete.")


if __name__ == "__main__":
    build_snapshot()
