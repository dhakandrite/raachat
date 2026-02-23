"""Vimshottari Dasha calculations."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

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
    """Convert sidereal years to approximate days."""
    return years * 365.2425


def build_vimshottari_periods(start_lord: str, birth_dt_utc: datetime, years: int = 120) -> list[DashaPeriod]:
    """Build Vimshottari Mahadasha, Antardasha, and Pratyantardasha periods.

    The function returns flat period objects carrying parent IDs for hierarchy.
    """
    periods: list[DashaPeriod] = []
    cursor = birth_dt_utc.astimezone(timezone.utc)
    if start_lord not in DASHA_ORDER:
        raise ValueError(f"Invalid dasha lord: {start_lord}")

    start_idx = DASHA_ORDER.index(start_lord)
    maha_sequence = DASHA_ORDER[start_idx:] + DASHA_ORDER[:start_idx]

    for maha_lord in maha_sequence:
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

            pratyantar_cursor = antar_cursor
            for pratyantar_lord in DASHA_ORDER:
                pratyantar_years = antar_years * DASHA_YEARS[pratyantar_lord] / 120
                pratyantar_end = pratyantar_cursor + timedelta(days=_years_to_days(pratyantar_years))
                pratyantar_id = (
                    f"pratyantar-{maha_lord}-{antar_lord}-{pratyantar_lord}-{pratyantar_cursor.date()}"
                )
                periods.append(
                    DashaPeriod(
                        id=pratyantar_id,
                        level="pratyantar",
                        lord=pratyantar_lord,
                        start_datetime=pratyantar_cursor,
                        end_datetime=pratyantar_end,
                        parent_ids=[maha_id, antar_id],
                    )
                )
                pratyantar_cursor = pratyantar_end

            antar_cursor = antar_end

        cursor = maha_end
        if (cursor - birth_dt_utc).days > _years_to_days(years):
            break
    return periods


def current_dasha_levels(
    periods: list[DashaPeriod],
    on_dt: datetime,
) -> tuple[DashaPeriod | None, DashaPeriod | None, DashaPeriod | None]:
    """Return current Mahadasha, Antardasha, and Pratyantardasha for a datetime."""
    maha = next(
        (p for p in periods if p.level == "maha" and p.start_datetime <= on_dt <= p.end_datetime),
        None,
    )
    antar = next(
        (
            p
            for p in periods
            if p.level == "antar"
            and p.start_datetime <= on_dt <= p.end_datetime
            and maha
            and maha.id in p.parent_ids
        ),
        None,
    )
    pratyantar = next(
        (
            p
            for p in periods
            if p.level == "pratyantar"
            and p.start_datetime <= on_dt <= p.end_datetime
            and maha
            and antar
            and maha.id in p.parent_ids
            and antar.id in p.parent_ids
        ),
        None,
    )
    return maha, antar, pratyantar


def current_dasha(periods: list[DashaPeriod], on_dt: datetime) -> tuple[DashaPeriod | None, DashaPeriod | None]:
    """Backward-compatible helper returning current Mahadasha + Antardasha."""
    maha, antar, _ = current_dasha_levels(periods, on_dt)
    return maha, antar


def dasha_lord_from_moon_nakshatra(moon_nakshatra_index: int) -> str:
    """Map Moon nakshatra index (0..26) to Vimshottari starting lord."""
    return DASHA_ORDER[moon_nakshatra_index % 9]
