"""Vimshottari Dasha calculations."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from itertools import cycle

from raajeeb_astro_prime.models.astro_core import DashaPeriod

DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17,
}


def _years_to_days(years: float) -> float:
    return years * 365.2425


def build_vimshottari_periods(start_lord: str, birth_dt_utc: datetime, years: int = 120) -> list[DashaPeriod]:
    """Build Mahadasha and Antardasha periods from a start lord."""
    periods: list[DashaPeriod] = []
    cursor = birth_dt_utc.astimezone(timezone.utc)
    start_idx = DASHA_ORDER.index(start_lord)
    lords = DASHA_ORDER[start_idx:] + DASHA_ORDER[:start_idx]

    for maha_lord in lords:
        maha_days = _years_to_days(DASHA_YEARS[maha_lord])
        maha_end = cursor + timedelta(days=maha_days)
        maha_id = f"maha-{maha_lord}-{cursor.date()}"
        periods.append(
            DashaPeriod(
                id=maha_id,
                level="maha",
                lord=maha_lord,
                start_datetime=cursor,
                end_datetime=maha_end,
                parent_ids=[],
            )
        )

        antar_cursor = cursor
        for antar_lord in DASHA_ORDER:
            antar_years = DASHA_YEARS[maha_lord] * DASHA_YEARS[antar_lord] / 120
            antar_end = antar_cursor + timedelta(days=_years_to_days(antar_years))
            antar_id = f"antar-{maha_lord}-{antar_lord}-{antar_cursor.date()}"
            periods.append(
                DashaPeriod(
                    id=antar_id,
                    level="antar",
                    lord=antar_lord,
                    start_datetime=antar_cursor,
                    end_datetime=antar_end,
                    parent_ids=[maha_id],
                )
            )
            antar_cursor = antar_end
        cursor = maha_end
        if (cursor - birth_dt_utc).days > _years_to_days(years):
            break
    return periods


def current_dasha(periods: list[DashaPeriod], on_dt: datetime) -> tuple[DashaPeriod | None, DashaPeriod | None]:
    """Return current maha and antar period for datetime."""
    maha = next((p for p in periods if p.level == "maha" and p.start_datetime <= on_dt <= p.end_datetime), None)
    antar = next((p for p in periods if p.level == "antar" and p.start_datetime <= on_dt <= p.end_datetime and maha and maha.id in p.parent_ids), None)
    return maha, antar


def dasha_lord_from_moon_nakshatra(moon_nakshatra_index: int) -> str:
    """Map moon nakshatra index to Vimshottari starting lord."""
    return list(cycle(DASHA_ORDER))[moon_nakshatra_index % 9]
