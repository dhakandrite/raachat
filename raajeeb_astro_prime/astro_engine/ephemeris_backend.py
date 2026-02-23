"""Ephemeris backend abstraction with Swiss Ephemeris and CSV fallback."""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

LOGGER = logging.getLogger(__name__)

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


@dataclass
class EphemerisResult:
    """Tropical longitude + speed result for one planet."""

    longitude: float
    speed: float | None = None


class BaseEphemerisBackend:
    """Interface for tropical planetary positions."""

    def get_positions(self, dt_utc: datetime) -> dict[str, EphemerisResult]:
        raise NotImplementedError


class SwissEphemerisBackend(BaseEphemerisBackend):
    """Use pyswisseph when installed."""

    SWISS_MAP = {
        "Sun": 0,
        "Moon": 1,
        "Mercury": 2,
        "Venus": 3,
        "Mars": 4,
        "Jupiter": 5,
        "Saturn": 6,
        "Rahu": 10,
    }

    def __init__(self) -> None:
        import swisseph as swe  # type: ignore

        self.swe = swe

    def get_positions(self, dt_utc: datetime) -> dict[str, EphemerisResult]:
        """Return tropical positions from Swiss Ephemeris."""
        jd = self.swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60)
        out: dict[str, EphemerisResult] = {}
        for planet, key in self.SWISS_MAP.items():
            data, _ = self.swe.calc_ut(jd, key)
            out[planet] = EphemerisResult(longitude=data[0] % 360.0, speed=data[3])
        out["Ketu"] = EphemerisResult(longitude=(out["Rahu"].longitude + 180.0) % 360.0, speed=-out["Rahu"].speed if out["Rahu"].speed else None)
        return out


class CsvEphemerisBackend(BaseEphemerisBackend):
    """Read precomputed tropical longitudes from local CSV file."""

    def __init__(self, csv_path: Path) -> None:
        self.csv_path = csv_path

    def get_positions(self, dt_utc: datetime) -> dict[str, EphemerisResult]:
        """Return nearest-day rows from CSV or deterministic fallback."""
        date_key = dt_utc.date().isoformat()
        rows: list[dict[str, str]] = []
        with self.csv_path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
        selected = next((row for row in rows if row["date"] == date_key), rows[0] if rows else None)
        if selected is None:
            raise ValueError("Ephemeris CSV is empty.")
        out: dict[str, EphemerisResult] = {}
        for planet in PLANETS:
            out[planet] = EphemerisResult(longitude=float(selected[planet]), speed=None)
        return out


def build_ephemeris_backend(csv_path: Path) -> BaseEphemerisBackend:
    """Return Swiss backend when available, else CSV backend."""
    try:
        backend = SwissEphemerisBackend()
        LOGGER.info("Using Swiss Ephemeris backend.")
        return backend
    except Exception as exc:  # pragma: no cover - import/runtime dependent
        LOGGER.warning("Swiss Ephemeris unavailable (%s). Falling back to CSV backend.", exc)
        return CsvEphemerisBackend(csv_path=csv_path)
