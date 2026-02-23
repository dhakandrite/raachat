"""Template renderer for offline deterministic narration."""

from __future__ import annotations

from raajeeb_astro_prime.models.compatibility import CompatibilityResult


def render_chart_summary(name: str, lagna: str, moon: str, yogas: list[dict[str, str]]) -> str:
    """Render chart summary in Ashwini Astrology voice."""
    yoga_line = ", ".join(y["name"] for y in yogas) if yogas else "No major predefined yoga triggered in demo rules"
    return (
        f"{name}, your chart opens with {lagna} Lagna and {moon} Moon. "
        f"Detected yogic signatures: {yoga_line}. "
        "This is reflective spiritual guidance, not medical, psychological, or financial advice."
    )


def render_dasha_now(maha: str, antar: str | None, pratyantar: str | None = None) -> str:
    """Render current dasha statement with optional pratyantardasha."""
    antar_text = antar or "(antar not found)"
    pratyantar_text = pratyantar or "(pratyantar not found)"
    return (
        f"Current cycle: {maha} Mahadasha, {antar_text} Antardasha, and "
        f"{pratyantar_text} Pratyantardasha influence."
    )


def render_transit(highlights: list[str]) -> str:
    """Render transit interpretation."""
    if not highlights:
        return "Gochar is steady today; focus on house activations and your running dasha context."
    return " | ".join(highlights)


def render_compatibility(result: CompatibilityResult) -> str:
    """Render compatibility summary text."""
    return f"Total Guna Milan score: {result.total_score_36}/36. {result.textual_summary}"
