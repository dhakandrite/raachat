"""Profile storage in local JSON file."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from raajeeb_astro_prime.models.astro_core import BirthDetails, Profile


class ProfileStore:
    """Simple local JSON profile repository."""

    def __init__(self, path: Path) -> None:
        self.path = path
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _read(self) -> list[Profile]:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return [Profile.model_validate(item) for item in raw]

    def _write(self, profiles: list[Profile]) -> None:
        self.path.write_text(json.dumps([p.model_dump(mode="json") for p in profiles], indent=2), encoding="utf-8")

    def create_profile(self, name: str, birth: BirthDetails) -> Profile:
        """Create and persist a profile."""
        profiles = self._read()
        profile = Profile(id=str(uuid4()), name=name, birth_details=birth)
        profiles.append(profile)
        self._write(profiles)
        return profile

    def list_profiles(self) -> list[Profile]:
        """Return all profiles."""
        return self._read()

    def get_by_name(self, name: str) -> Profile:
        """Find a profile by case-insensitive name."""
        profiles = self._read()
        for profile in profiles:
            if profile.name.lower() == name.lower():
                return profile
        raise ValueError(f"Profile not found: {name}")

    def upsert(self, profile: Profile) -> None:
        """Update profile object in storage."""
        profiles = self._read()
        updated = []
        replaced = False
        for existing in profiles:
            if existing.id == profile.id:
                updated.append(profile)
                replaced = True
            else:
                updated.append(existing)
        if not replaced:
            updated.append(profile)
        self._write(updated)
