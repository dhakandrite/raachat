"""Lookup advisory remedies and gemstones."""

from __future__ import annotations

import csv
from pathlib import Path


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    """Load CSV rows from local data file."""
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def remedies_for_planet(planet: str, remedies_rows: list[dict[str, str]]) -> list[str]:
    """Return soft-tone Lal Kitab style remedies for a planet."""
    return [r["advisory"] for r in remedies_rows if r["planet"].lower() == planet.lower()]


def gemstones_for_planet(planet: str, gemstone_rows: list[dict[str, str]]) -> list[str]:
    """Return gemstone suggestions with cautionary tone."""
    return [f"{r['gemstone']} ({r['note']})" for r in gemstone_rows if r["planet"].lower() == planet.lower()]
