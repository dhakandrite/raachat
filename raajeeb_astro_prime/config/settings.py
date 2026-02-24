"""Application settings and constants."""

from __future__ import annotations

from pathlib import Path
from pydantic import BaseModel, Field
from typing import Literal


class AppSettings(BaseModel):
    """Settings used by the local astrology assistant."""

    app_name: str = "Raajeeb AstroAlchemy Prime 2.0"
    codename: str = "Astro Logic Prime"
    sidereal_mode: str = "lahiri"
    house_system: str = "whole_sign"
    default_timezone: str = "Asia/Kolkata"
    profile_store: Path = Field(default_factory=lambda: Path("profiles.json"))
    ephemeris_csv: Path = Field(default_factory=lambda: Path("raajeeb_astro_prime/data/ephemeris.csv"))
    vedic_yogas_csv: Path = Field(default_factory=lambda: Path("raajeeb_astro_prime/data/vedic_yogas.csv"))
    remedies_csv: Path = Field(default_factory=lambda: Path("raajeeb_astro_prime/data/lal_kitab_remedies.csv"))
    remedies_matrix_csv: Path = Field(default_factory=lambda: Path("raajeeb_astro_prime/data/lalkitab_remedies_matrix.csv"))
    gemstones_csv: Path = Field(default_factory=lambda: Path("raajeeb_astro_prime/data/remedies_gemstones.csv"))
    persona_prompt_file: Path = Field(
        default_factory=lambda: Path("raajeeb_astro_prime/config/persona_system_prompt.txt")
    )
    llm_mode: Literal["auto", "gpt4all", "template"] = "auto"
    gpt4all_model_name: str = "Phi-3-mini-4k-instruct.Q4_0.gguf"
    gpt4all_model_path: Path = Field(default_factory=lambda: Path("models"))


def get_settings() -> AppSettings:
    """Return default app settings."""
    return AppSettings()
