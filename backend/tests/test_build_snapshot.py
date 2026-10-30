"""Tests for snapshot builder pipeline."""

import json
from pathlib import Path

import httpx
import pandas as pd

from ingestion.build_snapshot import build_snapshot
from ingestion.elexon_client import ElexonClient


def test_build_snapshot_writes_files(tmp_path: Path):
    """Verify build_snapshot creates actuals, forecasts, and metadata files."""
    def mock_handler(request: httpx.Request) -> httpx.Response:
        url_str = str(request.url)
        if "FUELHH" in url_str:
            return httpx.Response(
                200,
                json=[
                    {
                        "dataset": "FUELHH",
                        "startTime": "2026-01-02T00:00:00Z",
                        "generation": 11000.0,
                        "settlementDate": "2026-01-02",
                        "settlementPeriod": 1,
                    }
                ],
            )
        if "WINDFOR" in url_str:
            return httpx.Response(
                200,
                json=[
                    {
                        "dataset": "WINDFOR",
                        "publishTime": "2026-01-01T00:00:00Z",
                        "startTime": "2026-01-02T00:00:00Z",
                        "generation": 11500.0,
                    }
                ],
            )
        return httpx.Response(404)

    client = ElexonClient(transport=httpx.MockTransport(mock_handler))
    build_snapshot(output_dir=tmp_path, client=client)

    actuals_file = tmp_path / "actuals.parquet"
    forecasts_file = tmp_path / "forecasts.parquet"
    meta_file = tmp_path / "snapshot_meta.json"

    assert actuals_file.exists()
    assert forecasts_file.exists()
    assert meta_file.exists()

    df_act = pd.read_parquet(actuals_file)
    assert len(df_act) == 1
    assert df_act.iloc[0]["generation_mw"] == 11000.0

    df_fc = pd.read_parquet(forecasts_file)
    assert len(df_fc) == 1
    assert df_fc.iloc[0]["generation_mw"] == 11500.0
    assert df_fc.iloc[0]["horizon_h"] == 24.0

    with open(meta_file, encoding="utf-8") as f:
        meta = json.load(f)
    assert meta["actuals"]["row_count"] == 1
    assert meta["forecasts"]["row_count"] == 1
