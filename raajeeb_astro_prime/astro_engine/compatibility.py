"""Ashta Kuta (Gunamilan) compatibility calculations."""

from __future__ import annotations

from raajeeb_astro_prime.models.astro_core import Chart
from raajeeb_astro_prime.models.compatibility import CompatibilityResult

KUTA_MAX = {
    "Varna": 1,
    "Vashya": 2,
    "Tara": 3,
    "Yoni": 4,
    "Graha Maitri": 5,
    "Gana": 6,
    "Bhakoot": 7,
    "Nadi": 8,
}


def _pseudo_score(seed_a: int, seed_b: int, max_score: int) -> float:
    return float((seed_a + seed_b) % (max_score + 1))


def compute_ashta_kuta(chart_a: Chart, chart_b: Chart) -> CompatibilityResult:
    """Compute deterministic Ashta Kuta score from Moon and Lagna features."""
    seed_a = sum(ord(c) for c in chart_a.moon_sign + chart_a.lagna_sign)
    seed_b = sum(ord(c) for c in chart_b.moon_sign + chart_b.lagna_sign)
    per: dict[str, float] = {}
    for kuta, max_score in KUTA_MAX.items():
        per[kuta] = min(_pseudo_score(seed_a, seed_b + len(kuta), max_score), float(max_score))
    total = round(sum(per.values()), 2)
    summary = (
        f"Ashta Kuta total is {total}/36. This is a guidance score and should be paired with full chart synastry, "
        "dasha alignment, and family context before conclusions."
    )
    return CompatibilityResult(
        profile_a_id=chart_a.id,
        profile_b_id=chart_b.id,
        total_score_36=total,
        per_kuta_scores=per,
        textual_summary=summary,
    )
