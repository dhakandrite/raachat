"""Deterministic Vedic astrology calculations."""

from __future__ import annotations

from datetime import datetime, timezone
from math import floor
from zoneinfo import ZoneInfo

SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati",
]


def normalize_degrees(value: float) -> float:
    """Normalize degrees to [0, 360)."""
    return value % 360.0


def tropical_to_sidereal(tropical_longitude: float, ayanamsa: float) -> float:
    """Convert tropical longitude to sidereal longitude."""
    return normalize_degrees(tropical_longitude - ayanamsa)


def approximate_lahiri_ayanamsa(dt_utc: datetime) -> float:
    """Approximate Lahiri ayanamsa in degrees for modern dates."""
    base = 23.8531  # around J2000
    years = (dt_utc.year + (dt_utc.timetuple().tm_yday / 365.25)) - 2000.0
    return base + years * 0.013968


def sign_from_longitude(longitude: float) -> str:
    """Return rashi sign from longitude."""
    return SIGNS[int(normalize_degrees(longitude) // 30)]


def house_from_lagna(planet_sign: str, lagna_sign: str) -> int:
    """Return whole-sign house number relative to Lagna sign."""
    p_idx = SIGNS.index(planet_sign)
    l_idx = SIGNS.index(lagna_sign)
    return ((p_idx - l_idx) % 12) + 1


def nakshatra_and_pada(longitude: float) -> tuple[str, int]:
    """Return nakshatra name and pada from sidereal longitude."""
    seg = 13.3333333333
    n_index = int(normalize_degrees(longitude) // seg)
    within = normalize_degrees(longitude) % seg
    pada = int(within // (seg / 4)) + 1
    return NAKSHATRAS[n_index], min(pada, 4)


def to_utc_datetime(date_str: str, time_str: str, timezone_name: str) -> datetime:
    """Convert local date/time into UTC datetime."""
    local_dt = datetime.fromisoformat(f"{date_str}T{time_str}").replace(tzinfo=ZoneInfo(timezone_name))
    return local_dt.astimezone(timezone.utc)


def julian_day(dt_utc: datetime) -> float:
    """Compute Julian day number (UTC)."""
    y = dt_utc.year
    m = dt_utc.month
    d = dt_utc.day + (dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600) / 24
    if m <= 2:
        y -= 1
        m += 12
    a = floor(y / 100)
    b = 2 - a + floor(a / 4)
    return floor(365.25 * (y + 4716)) + floor(30.6001 * (m + 1)) + d + b - 1524.5


def approximate_lagna_longitude(dt_utc: datetime, longitude: float, latitude: float) -> float:
    """Approximate ascendant longitude using local sidereal time.

    This is intentionally simple and deterministic for offline mode.
    """
    jd = julian_day(dt_utc)
    t = (jd - 2451545.0) / 36525.0
    gmst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * t**2
    lst = normalize_degrees(gmst + longitude)
    correction = latitude * 0.1
    return normalize_degrees(lst + correction)
