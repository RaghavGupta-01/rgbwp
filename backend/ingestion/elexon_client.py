"""Elexon BMRS API client for FUELHH actuals and WINDFOR forecasts."""

from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"


def _is_retryable_error(exc: BaseException) -> bool:
    """Determine whether an HTTP exception should trigger a retry."""
    if isinstance(exc, httpx.RequestError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code >= 500 or exc.response.status_code == 429
    return False


class ElexonClient:
    """Client for fetching generation datasets from Elexon BMRS."""

    def __init__(
        self,
        base_url: str = BASE_URL,
        timeout: float = 60.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.transport = transport

    @retry(
        retry=retry_if_exception(_is_retryable_error),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    def _fetch_stream(
        self,
        dataset: str,
        params: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Fetch records from a dataset stream endpoint with retries."""
        url = f"{self.base_url}/datasets/{dataset}/stream"
        headers = {"Accept": "application/json"}

        with httpx.Client(
            timeout=self.timeout, transport=self.transport
        ) as client:
            response = client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return []

    def fetch_actuals_fuelhh(
        self,
        date_from: date | str,
        date_to: date | str,
        fuel_type: str = "WIND",
        chunk_days: int = 7,
    ) -> List[Dict[str, Any]]:
        """Fetch half-hourly generation actuals in date chunks."""
        start_d = (
            datetime.strptime(date_from, "%Y-%m-%d").date()
            if isinstance(date_from, str)
            else date_from
        )
        end_d = (
            datetime.strptime(date_to, "%Y-%m-%d").date()
            if isinstance(date_to, str)
            else date_to
        )

        all_records: List[Dict[str, Any]] = []
        curr_d = start_d

        while curr_d <= end_d:
            next_d = min(curr_d + timedelta(days=chunk_days - 1), end_d)
            params = {
                "settlementDateFrom": curr_d.isoformat(),
                "settlementDateTo": next_d.isoformat(),
                "fuelType": fuel_type,
            }
            records = self._fetch_stream("FUELHH", params)
            all_records.extend(records)
            curr_d = next_d + timedelta(days=1)

        return all_records

    def fetch_forecasts_windfor(
        self,
        publish_from: datetime | str,
        publish_to: datetime | str,
        chunk_days: int = 2,
    ) -> List[Dict[str, Any]]:
        """Fetch hourly wind forecasts chunked by publication window."""
        start_dt = (
            datetime.fromisoformat(publish_from.replace("Z", "+00:00"))
            if isinstance(publish_from, str)
            else publish_from
        )
        end_dt = (
            datetime.fromisoformat(publish_to.replace("Z", "+00:00"))
            if isinstance(publish_to, str)
            else publish_to
        )

        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc)
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)

        all_records: List[Dict[str, Any]] = []
        curr_dt = start_dt

        while curr_dt < end_dt:
            next_dt = min(curr_dt + timedelta(days=chunk_days), end_dt)
            params = {
                "publishDateTimeFrom": curr_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "publishDateTimeTo": next_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            records = self._fetch_stream("WINDFOR", params)
            all_records.extend(records)
            curr_dt = next_dt

        return all_records
