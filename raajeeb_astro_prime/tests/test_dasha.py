"""Unit tests for Vimshottari dasha engine."""

from __future__ import annotations

from datetime import datetime, timezone
import unittest

try:
    from raajeeb_astro_prime.astro_engine.dasha import (
        DASHA_ORDER,
        build_vimshottari_periods,
        current_dasha_levels,
        dasha_lord_from_moon_nakshatra,
    )
except ModuleNotFoundError as exc:  # pragma: no cover - environment dependency
    raise unittest.SkipTest(f"Required dependency missing: {exc}") from exc



class DashaEngineTests(unittest.TestCase):
    """Validate dasha period generation and lookup."""

    def test_start_lord_mapping_cycles_every_nine_nakshatras(self) -> None:
        self.assertEqual(dasha_lord_from_moon_nakshatra(0), DASHA_ORDER[0])
        self.assertEqual(dasha_lord_from_moon_nakshatra(8), DASHA_ORDER[8])
        self.assertEqual(dasha_lord_from_moon_nakshatra(9), DASHA_ORDER[0])
        self.assertEqual(dasha_lord_from_moon_nakshatra(26), DASHA_ORDER[8])

    def test_generates_all_three_levels(self) -> None:
        birth = datetime(2000, 1, 1, tzinfo=timezone.utc)
        periods = build_vimshottari_periods("Ketu", birth, years=1)
        levels = {p.level for p in periods}
        self.assertIn("maha", levels)
        self.assertIn("antar", levels)
        self.assertIn("pratyantar", levels)

    def test_current_dasha_levels_link_hierarchy(self) -> None:
        birth = datetime(2000, 1, 1, tzinfo=timezone.utc)
        periods = build_vimshottari_periods("Ketu", birth, years=2)
        on_dt = datetime(2000, 6, 1, tzinfo=timezone.utc)
        maha, antar, pratyantar = current_dasha_levels(periods, on_dt)

        self.assertIsNotNone(maha)
        self.assertIsNotNone(antar)
        self.assertIsNotNone(pratyantar)
        assert maha and antar and pratyantar
        self.assertIn(maha.id, antar.parent_ids)
        self.assertIn(maha.id, pratyantar.parent_ids)
        self.assertIn(antar.id, pratyantar.parent_ids)


if __name__ == "__main__":
    unittest.main()
