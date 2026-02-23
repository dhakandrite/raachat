"""Yoga detection from chart placements and CSV definitions."""

from __future__ import annotations

import csv
from pathlib import Path

from raajeeb_astro_prime.models.astro_core import Chart


def load_yoga_rules(csv_path: Path) -> list[dict[str, str]]:
    """Load yoga rules from CSV."""
    with csv_path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def detect_yogas(chart: Chart, yoga_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Detect simple yogas from conjunction and house rules."""
    placements = {p.planet_name: p for p in chart.planet_positions}
    found: list[dict[str, str]] = []

    for rule in yoga_rows:
        planets = [x.strip() for x in rule["planets"].split("+")]
        if all(p in placements for p in planets):
            if rule["condition"] == "same_house":
                houses = {placements[p].house for p in planets}
                if len(houses) == 1:
                    found.append(rule)
            elif rule["condition"].startswith("house_"):
                target_house = int(rule["condition"].split("_")[1])
                if all(placements[p].house == target_house for p in planets):
                    found.append(rule)
    return found
