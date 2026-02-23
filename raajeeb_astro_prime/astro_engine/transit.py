"""Transit (Gochar) calculations and highlights."""

from __future__ import annotations

from datetime import datetime

from raajeeb_astro_prime.models.astro_core import Chart, TransitPosition, TransitSnapshot
from .vedic_calculations import house_from_lagna, sign_from_longitude


def compute_transit_snapshot(
    chart: Chart,
    transit_positions: dict[str, float],
    transit_date: datetime,
) -> TransitSnapshot:
    """Compute transit houses from natal Lagna and Moon."""
    moon_sign = chart.moon_sign
    positions: list[TransitPosition] = []
    highlights: list[str] = []

    for planet, lon in transit_positions.items():
        sign = sign_from_longitude(lon)
        h_lagna = house_from_lagna(sign, chart.lagna_sign)
        h_moon = house_from_lagna(sign, moon_sign)
        positions.append(
            TransitPosition(
                planet_name=planet,
                sidereal_longitude=lon,
                sign=sign,
                house_from_lagna=h_lagna,
                house_from_moon=h_moon,
            )
        )
        if planet == "Saturn" and h_moon in {12, 1, 2}:
            highlights.append("Saturn is in Sade Sati zone from natal Moon (12/1/2 houses).")
        if planet == "Jupiter" and h_lagna in {1, 5, 9}:
            highlights.append("Jupiter transit activates trinal houses from Lagna (1/5/9).")
    return TransitSnapshot(date=transit_date.date(), positions=positions, highlights=highlights)
