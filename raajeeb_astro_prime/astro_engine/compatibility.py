"""Ashta Kuta (Gunamilan) compatibility calculations."""

from __future__ import annotations

from raajeeb_astro_prime.astro_engine.vedic_calculations import NAKSHATRAS, SIGNS
from raajeeb_astro_prime.models.astro_core import Chart
from raajeeb_astro_prime.models.compatibility import CompatibilityResult

KUTA_MAX = {
    "Varna": 1.0,
    "Vashya": 2.0,
    "Tara": 3.0,
    "Yoni": 4.0,
    "Graha Maitri": 5.0,
    "Gana": 6.0,
    "Bhakoot": 7.0,
    "Nadi": 8.0,
}

SIGN_LORDS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

# Planetary friendship reference used for Graha Maitri scoring.
FRIENDSHIP = {
    "Sun": {"friends": {"Moon", "Mars", "Jupiter"}, "neutral": {"Mercury"}},
    "Moon": {"friends": {"Sun", "Mercury"}, "neutral": {"Mars", "Jupiter", "Venus", "Saturn"}},
    "Mars": {"friends": {"Sun", "Moon", "Jupiter"}, "neutral": {"Venus", "Saturn"}},
    "Mercury": {"friends": {"Sun", "Venus"}, "neutral": {"Mars", "Jupiter", "Saturn"}},
    "Jupiter": {"friends": {"Sun", "Moon", "Mars"}, "neutral": {"Saturn"}},
    "Venus": {"friends": {"Mercury", "Saturn"}, "neutral": {"Mars", "Jupiter"}},
    "Saturn": {"friends": {"Mercury", "Venus"}, "neutral": {"Jupiter"}},
}

VARNA_BY_SIGN = {
    "Aries": "Kshatriya",
    "Taurus": "Vaishya",
    "Gemini": "Shudra",
    "Cancer": "Brahmin",
    "Leo": "Kshatriya",
    "Virgo": "Vaishya",
    "Libra": "Shudra",
    "Scorpio": "Brahmin",
    "Sagittarius": "Kshatriya",
    "Capricorn": "Vaishya",
    "Aquarius": "Shudra",
    "Pisces": "Brahmin",
}
VARNA_RANK = {"Shudra": 1, "Vaishya": 2, "Kshatriya": 3, "Brahmin": 4}

VASHYA_BY_SIGN = {
    "Aries": "Chatushpada",
    "Taurus": "Chatushpada",
    "Gemini": "Manava",
    "Cancer": "Jalachara",
    "Leo": "Vanachara",
    "Virgo": "Manava",
    "Libra": "Manava",
    "Scorpio": "Keeta",
    "Sagittarius": "Chatushpada",
    "Capricorn": "Chatushpada",
    "Aquarius": "Manava",
    "Pisces": "Jalachara",
}

GANA_CYCLE = ["Deva", "Manushya", "Rakshasa"]
NADI_CYCLE = ["Adi", "Madhya", "Antya"]
YONI_GROUPS = [
    "Horse",
    "Elephant",
    "Sheep",
    "Serpent",
    "Dog",
    "Cat",
    "Rat",
    "Cow",
    "Buffalo",
    "Tiger",
    "Hare",
    "Monkey",
    "Mongoose",
    "Lion",
]


def _moon_position(chart: Chart):
    return next(p for p in chart.planet_positions if p.planet_name == "Moon")


def _sign_distance(sign_a: str, sign_b: str) -> int:
    a = SIGNS.index(sign_a)
    b = SIGNS.index(sign_b)
    return ((b - a) % 12) + 1


def _varna_score(sign_a: str, sign_b: str) -> float:
    return 1.0 if VARNA_RANK[VARNA_BY_SIGN[sign_a]] <= VARNA_RANK[VARNA_BY_SIGN[sign_b]] else 0.0


def _vashya_score(sign_a: str, sign_b: str) -> float:
    return 2.0 if VASHYA_BY_SIGN[sign_a] == VASHYA_BY_SIGN[sign_b] else 1.0


def _tara_score(nak_a: int, nak_b: int) -> float:
    d1 = ((nak_b - nak_a) % 27) + 1
    d2 = ((nak_a - nak_b) % 27) + 1
    bad_remainders = {0, 3, 5}
    good_a = (d1 % 9) not in bad_remainders
    good_b = (d2 % 9) not in bad_remainders
    return 3.0 if good_a and good_b else 1.5 if good_a or good_b else 0.0


def _yoni_score(nak_a: int, nak_b: int) -> float:
    yoni_a = YONI_GROUPS[nak_a % len(YONI_GROUPS)]
    yoni_b = YONI_GROUPS[nak_b % len(YONI_GROUPS)]
    return 4.0 if yoni_a == yoni_b else 2.0


def _graha_maitri_score(sign_a: str, sign_b: str) -> float:
    lord_a = SIGN_LORDS[sign_a]
    lord_b = SIGN_LORDS[sign_b]
    if lord_a == lord_b:
        return 5.0
    if lord_b in FRIENDSHIP[lord_a]["friends"] and lord_a in FRIENDSHIP[lord_b]["friends"]:
        return 5.0
    if lord_b in FRIENDSHIP[lord_a]["neutral"] and lord_a in FRIENDSHIP[lord_b]["neutral"]:
        return 3.0
    return 1.0


def _gana_score(nak_a: int, nak_b: int) -> float:
    gana_a = GANA_CYCLE[nak_a % 3]
    gana_b = GANA_CYCLE[nak_b % 3]
    if gana_a == gana_b:
        return 6.0
    if {gana_a, gana_b} == {"Deva", "Manushya"}:
        return 5.0
    if {gana_a, gana_b} == {"Manushya", "Rakshasa"}:
        return 1.0
    return 0.0


def _bhakoot_score(sign_a: str, sign_b: str) -> float:
    distance = _sign_distance(sign_a, sign_b)
    return 0.0 if distance in {2, 6, 8, 12} else 7.0


def _nadi_score(nak_a: int, nak_b: int) -> float:
    nadi_a = NADI_CYCLE[nak_a % 3]
    nadi_b = NADI_CYCLE[nak_b % 3]
    return 0.0 if nadi_a == nadi_b else 8.0


def compute_ashta_kuta(chart_a: Chart, chart_b: Chart) -> CompatibilityResult:
    """Compute Ashta Kuta score from Moon sign and nakshatra attributes."""
    moon_a = _moon_position(chart_a)
    moon_b = _moon_position(chart_b)
    nak_a = NAKSHATRAS.index(moon_a.nakshatra_name)
    nak_b = NAKSHATRAS.index(moon_b.nakshatra_name)

    per: dict[str, float] = {
        "Varna": _varna_score(chart_a.moon_sign, chart_b.moon_sign),
        "Vashya": _vashya_score(chart_a.moon_sign, chart_b.moon_sign),
        "Tara": _tara_score(nak_a, nak_b),
        "Yoni": _yoni_score(nak_a, nak_b),
        "Graha Maitri": _graha_maitri_score(chart_a.moon_sign, chart_b.moon_sign),
        "Gana": _gana_score(nak_a, nak_b),
        "Bhakoot": _bhakoot_score(chart_a.moon_sign, chart_b.moon_sign),
        "Nadi": _nadi_score(nak_a, nak_b),
    }
    for kuta, max_score in KUTA_MAX.items():
        per[kuta] = min(max(per[kuta], 0.0), max_score)

    total = round(sum(per.values()), 2)
    summary = (
        f"Ashta Kuta score is {total}/36. Use this as one compatibility lens, then verify with full chart "
        "matching, dasha synchronization, and practical life values before making decisions."
    )
    return CompatibilityResult(
        profile_a_id=chart_a.id,
        profile_b_id=chart_b.id,
        total_score_36=total,
        per_kuta_scores=per,
        textual_summary=summary,
    )
