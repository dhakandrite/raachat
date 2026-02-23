"""Core Pydantic models for astrology calculations."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Literal, Optional
from pydantic import BaseModel, Field


class BirthDetails(BaseModel):
    """Birth input required for D1 chart construction."""

    date_of_birth: date
    time_of_birth: time
    timezone: str
    latitude: float
    longitude: float
    gender: Optional[str] = None
    notes: Optional[str] = None


class PlanetPosition(BaseModel):
    """Planet placement in sidereal Vedic framework."""

    planet_name: str
    sidereal_longitude: float = Field(ge=0.0, lt=360.0)
    sign: str
    house: int = Field(ge=1, le=12)
    nakshatra_name: str
    nakshatra_pada: int = Field(ge=1, le=4)
    speed: Optional[float] = None


class Chart(BaseModel):
    """Primary Rashi chart model."""

    id: str
    name: str
    birth_details: BirthDetails
    lagna_sign: str
    moon_sign: str
    sun_sign: str
    planet_positions: list[PlanetPosition]


class DashaPeriod(BaseModel):
    """Vimshottari period at maha/antar/pratyantar levels."""

    id: str
    level: Literal["maha", "antar", "pratyantar"]
    lord: str
    start_datetime: datetime
    end_datetime: datetime
    parent_ids: list[str] = Field(default_factory=list)


class TransitPosition(BaseModel):
    """Transit planet mapped relative to natal chart."""

    planet_name: str
    sidereal_longitude: float
    sign: str
    house_from_lagna: int
    house_from_moon: int


class TransitSnapshot(BaseModel):
    """Transit data for one date."""

    date: date
    positions: list[TransitPosition]
    highlights: list[str] = Field(default_factory=list)


class Profile(BaseModel):
    """Stored user profile and computed chart data."""

    id: str
    name: str
    birth_details: BirthDetails
    chart: Optional[Chart] = None
