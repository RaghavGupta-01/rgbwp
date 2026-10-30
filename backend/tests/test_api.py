"""Comprehensive integration tests for all backend API endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify health probe returns status ok."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_meta_endpoint():
    """Verify /api/meta returns data coverage and configuration."""
    resp = client.get("/api/meta")
    assert resp.status_code == 200
    data = resp.json()
    assert data["decision_date_from"] == "2026-01-01"
    assert data["delivery_date_from"] == "2026-01-02"
    assert data["delivery_date_to"] == "2026-02-01"
    assert data["default_cutoff_time"] == "09:00"
    assert data["actuals_row_count"] > 1000
    assert data["forecasts_row_count"] > 10000


def test_forecasts_decision_endpoint():
    """Verify /api/forecasts/decision returns 24 hourly points with band and kpis."""
    resp = client.get("/api/forecasts/decision?date=2026-01-02&cutoff=09:00")
    assert resp.status_code == 200
    data = resp.json()
    assert data["delivery_date"] == "2026-01-02"
    assert data["cutoff_time"] == "09:00"
    assert len(data["points"]) == 24
    assert "forecast_peak_mw" in data["kpis"]

    first_point = data["points"][0]
    assert "forecast_mw" in first_point
    assert "band_lower_mw" in first_point
    assert "band_upper_mw" in first_point


def test_forecast_versions_endpoint():
    """Verify /api/forecasts/versions returns revisions list."""
    resp = client.get("/api/forecasts/versions?date=2026-01-02")
    assert resp.status_code == 200
    data = resp.json()
    assert data["delivery_date"] == "2026-01-02"
    assert len(data["versions"]) > 0


def test_metrics_summary_endpoint():
    """Verify /api/metrics/summary returns accuracy KPIs."""
    resp = client.get("/api/metrics/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["n_hours"] > 0
    assert "mae" in data
    assert "rmse" in data
    assert "bias" in data
    assert "signed_p10" in data
    assert "signed_p90" in data


def test_metrics_breakdowns():
    """Verify daily, by-hour, by-horizon, by-level, and errors endpoints."""
    r_daily = client.get("/api/metrics/daily")
    assert r_daily.status_code == 200
    assert len(r_daily.json()) > 0

    r_hour = client.get("/api/metrics/by-hour")
    assert r_hour.status_code == 200
    assert len(r_hour.json()) == 24

    r_horiz = client.get("/api/metrics/by-horizon")
    assert r_horiz.status_code == 200
    assert len(r_horiz.json()) > 0

    r_level = client.get("/api/metrics/by-level")
    assert r_level.status_code == 200
    assert len(r_level.json()) > 0

    r_err = client.get("/api/metrics/errors")
    assert r_err.status_code == 200
    assert len(r_err.json()) > 0
