"""Unit tests for Ashta Kuta scoring."""

from __future__ import annotations

from datetime import date, time
import unittest

try:
    from raajeeb_astro_prime.astro_engine.compatibility import KUTA_MAX, compute_ashta_kuta
    from raajeeb_astro_prime.models.astro_core import BirthDetails, Chart, PlanetPosition
except ModuleNotFoundError as exc:  # pragma: no cover - environment dependency
    raise unittest.SkipTest(f"Required dependency missing: {exc}") from exc



def _chart(chart_id: str, moon_sign: str, moon_nak: str) -> Chart:
    birth = BirthDetails(
        date_of_birth=date(1990, 1, 1),
        time_of_birth=time(12, 0),
        timezone="Asia/Kolkata",
        latitude=23.0,
        longitude=90.0,
    )
    moon = PlanetPosition(
        planet_name="Moon",
        sidereal_longitude=10.0,
        sign=moon_sign,
        house=1,
        nakshatra_name=moon_nak,
        nakshatra_pada=1,
        speed=None,
    )
    return Chart(
        id=chart_id,
        name=chart_id,
        birth_details=birth,
        lagna_sign="Aries",
        moon_sign=moon_sign,
        sun_sign="Aries",
        planet_positions=[moon],
    )


class CompatibilityTests(unittest.TestCase):
    """Validate compatibility output contract and score bounds."""

    def test_scores_are_bounded(self) -> None:
        a = _chart("a", "Aries", "Ashwini")
        b = _chart("b", "Cancer", "Pushya")
        result = compute_ashta_kuta(a, b)

        self.assertLessEqual(result.total_score_36, 36.0)
        self.assertGreaterEqual(result.total_score_36, 0.0)
        self.assertEqual(set(result.per_kuta_scores.keys()), set(KUTA_MAX.keys()))
        for kuta, score in result.per_kuta_scores.items():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, KUTA_MAX[kuta])

    def test_identical_moon_signature_has_nonzero_score(self) -> None:
        a = _chart("a", "Taurus", "Rohini")
        b = _chart("b", "Taurus", "Rohini")
        result = compute_ashta_kuta(a, b)
        self.assertGreater(result.total_score_36, 0.0)


if __name__ == "__main__":
    unittest.main()
