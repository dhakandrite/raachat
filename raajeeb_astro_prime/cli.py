"""Typer CLI for Raajeeb AstroAlchemy Prime 2.0."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import typer

from raajeeb_astro_prime.astro_engine.compatibility import compute_ashta_kuta
from raajeeb_astro_prime.astro_engine.dasha import (
    build_vimshottari_periods,
    current_dasha_levels,
    dasha_lord_from_moon_nakshatra,
)
from raajeeb_astro_prime.astro_engine.ephemeris_backend import build_ephemeris_backend
from raajeeb_astro_prime.astro_engine.transit import compute_transit_snapshot
from raajeeb_astro_prime.astro_engine.vedic_calculations import (
    approximate_lahiri_ayanamsa,
    approximate_lagna_longitude,
    house_from_lagna,
    nakshatra_and_pada,
    sign_from_longitude,
    to_utc_datetime,
    tropical_to_sidereal,
)
from raajeeb_astro_prime.astro_engine.yogas import detect_yogas, load_yoga_rules
from raajeeb_astro_prime.config.settings import get_settings
from raajeeb_astro_prime.llm.gpt4all_client import GPT4AllClient
from raajeeb_astro_prime.llm.renderer import (
    render_chart_summary,
    render_compatibility,
    render_dasha_now,
    render_transit,
)
from raajeeb_astro_prime.models.astro_core import BirthDetails, Chart, PlanetPosition
from raajeeb_astro_prime.storage.profiles import ProfileStore

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOGGER = logging.getLogger(__name__)

app = typer.Typer(help="Raajeeb AstroAlchemy Prime 2.0 (Astro Logic Prime)")
profile_app = typer.Typer(help="Profile management commands")
chart_app = typer.Typer(help="Chart view commands")
dasha_app = typer.Typer(help="Vimshottari dasha commands")
app.add_typer(profile_app, name="profile")
app.add_typer(chart_app, name="chart")
app.add_typer(dasha_app, name="dasha")


def _load_persona_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _build_chart(name: str, birth: BirthDetails) -> Chart:
    settings = get_settings()
    backend = build_ephemeris_backend(settings.ephemeris_csv)
    dt_utc = to_utc_datetime(str(birth.date_of_birth), birth.time_of_birth.isoformat(), birth.timezone)
    ayanamsa = approximate_lahiri_ayanamsa(dt_utc)
    tropical = backend.get_positions(dt_utc)

    lagna_tropical = approximate_lagna_longitude(dt_utc, birth.longitude, birth.latitude)
    lagna_sidereal = tropical_to_sidereal(lagna_tropical, ayanamsa)
    lagna_sign = sign_from_longitude(lagna_sidereal)

    positions: list[PlanetPosition] = []
    for planet, data in tropical.items():
        sidereal = tropical_to_sidereal(data.longitude, ayanamsa)
        sign = sign_from_longitude(sidereal)
        house = house_from_lagna(sign, lagna_sign)
        nak, pada = nakshatra_and_pada(sidereal)
        positions.append(
            PlanetPosition(
                planet_name=planet,
                sidereal_longitude=round(sidereal, 4),
                sign=sign,
                house=house,
                nakshatra_name=nak,
                nakshatra_pada=pada,
                speed=data.speed,
            )
        )
    moon_sign = next(p.sign for p in positions if p.planet_name == "Moon")
    sun_sign = next(p.sign for p in positions if p.planet_name == "Sun")
    return Chart(
        id=f"chart-{name.lower().replace(' ', '-')}",
        name=name,
        birth_details=birth,
        lagna_sign=lagna_sign,
        moon_sign=moon_sign,
        sun_sign=sun_sign,
        planet_positions=positions,
    )


@profile_app.command("create")
def profile_create(
    name: str = typer.Option(..., prompt=True),
    date_of_birth: str = typer.Option(..., prompt=True, help="YYYY-MM-DD"),
    time_of_birth: str = typer.Option(..., prompt=True, help="HH:MM"),
    timezone_name: str = typer.Option("Asia/Kolkata", prompt=True),
    latitude: float = typer.Option(..., prompt=True),
    longitude: float = typer.Option(..., prompt=True),
    gender: Optional[str] = typer.Option(None),
    notes: Optional[str] = typer.Option(None),
) -> None:
    """Create a new birth profile and computed chart."""
    settings = get_settings()
    store = ProfileStore(settings.profile_store)
    birth = BirthDetails(
        date_of_birth=datetime.strptime(date_of_birth, "%Y-%m-%d").date(),
        time_of_birth=datetime.strptime(time_of_birth, "%H:%M").time(),
        timezone=timezone_name,
        latitude=latitude,
        longitude=longitude,
        gender=gender,
        notes=notes,
    )
    profile = store.create_profile(name, birth)
    profile.chart = _build_chart(name, birth)
    store.upsert(profile)
    typer.echo(f"Created profile: {profile.name} ({profile.id})")


@profile_app.command("list")
def profile_list() -> None:
    """List all stored profiles."""
    store = ProfileStore(get_settings().profile_store)
    for profile in store.list_profiles():
        typer.echo(f"- {profile.name} [{profile.id}]")


@chart_app.command("summary")
def chart_summary(profile: str = typer.Option(..., "--profile")) -> None:
    """Show chart summary with yogas."""
    settings = get_settings()
    store = ProfileStore(settings.profile_store)
    prof = store.get_by_name(profile)
    if prof.chart is None:
        prof.chart = _build_chart(prof.name, prof.birth_details)
        store.upsert(prof)
    yogas = detect_yogas(prof.chart, load_yoga_rules(settings.vedic_yogas_csv))
    typer.echo(render_chart_summary(prof.name, prof.chart.lagna_sign, prof.chart.moon_sign, yogas))


@chart_app.command("placements")
def chart_placements(profile: str = typer.Option(..., "--profile")) -> None:
    """Print placements in a tabular text layout."""
    store = ProfileStore(get_settings().profile_store)
    prof = store.get_by_name(profile)
    if prof.chart is None:
        prof.chart = _build_chart(prof.name, prof.birth_details)
        store.upsert(prof)
    typer.echo("planet | sign | degree | house | nakshatra | pada")
    for p in prof.chart.planet_positions:
        typer.echo(
            f"{p.planet_name:8} | {p.sign:11} | {p.sidereal_longitude:7.2f} | {p.house:5} | {p.nakshatra_name:15} | {p.nakshatra_pada}"
        )


@dasha_app.command("timeline")
def dasha_timeline(
    profile: str = typer.Option(..., "--profile"),
    from_date: str = typer.Option(..., "--from"),
    to_date: str = typer.Option(..., "--to"),
) -> None:
    """Show Vimshottari dasha rows between date range."""
    store = ProfileStore(get_settings().profile_store)
    prof = store.get_by_name(profile)
    if prof.chart is None:
        prof.chart = _build_chart(prof.name, prof.birth_details)
        store.upsert(prof)
    moon_lon = next(p.sidereal_longitude for p in prof.chart.planet_positions if p.planet_name == "Moon")
    nak_idx = int(moon_lon // 13.3333333333)
    start_lord = dasha_lord_from_moon_nakshatra(nak_idx)
    birth_utc = to_utc_datetime(str(prof.birth_details.date_of_birth), prof.birth_details.time_of_birth.isoformat(), prof.birth_details.timezone)
    periods = build_vimshottari_periods(start_lord, birth_utc)

    f = datetime.strptime(from_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    t = datetime.strptime(to_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    for period in periods:
        if period.start_datetime <= t and period.end_datetime >= f:
            typer.echo(f"{period.level:10} {period.lord:8} {period.start_datetime.date()} -> {period.end_datetime.date()}")


@dasha_app.command("now")
def dasha_now(profile: str = typer.Option(..., "--profile"), on: Optional[str] = typer.Option(None, "--on")) -> None:
    """Show running Mahadasha and Antardasha for date."""
    store = ProfileStore(get_settings().profile_store)
    prof = store.get_by_name(profile)
    if prof.chart is None:
        prof.chart = _build_chart(prof.name, prof.birth_details)
        store.upsert(prof)
    moon_lon = next(p.sidereal_longitude for p in prof.chart.planet_positions if p.planet_name == "Moon")
    nak_idx = int(moon_lon // 13.3333333333)
    start_lord = dasha_lord_from_moon_nakshatra(nak_idx)
    birth_utc = to_utc_datetime(str(prof.birth_details.date_of_birth), prof.birth_details.time_of_birth.isoformat(), prof.birth_details.timezone)
    periods = build_vimshottari_periods(start_lord, birth_utc)

    on_dt = datetime.strptime(on, "%Y-%m-%d").replace(tzinfo=timezone.utc) if on else datetime.now(timezone.utc)
    maha, antar, pratyantar = current_dasha_levels(periods, on_dt)
    typer.echo(
        render_dasha_now(
            maha.lord if maha else "Unknown",
            antar.lord if antar else None,
            pratyantar.lord if pratyantar else None,
        )
    )


@app.command("transit")
def transit(profile: str = typer.Option(..., "--profile"), date: str = typer.Option(..., "--date")) -> None:
    """Compute gochar snapshot and textual highlights."""
    settings = get_settings()
    store = ProfileStore(settings.profile_store)
    prof = store.get_by_name(profile)
    if prof.chart is None:
        prof.chart = _build_chart(prof.name, prof.birth_details)
        store.upsert(prof)

    dt = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    backend = build_ephemeris_backend(settings.ephemeris_csv)
    ay = approximate_lahiri_ayanamsa(dt)
    tropical = backend.get_positions(dt)
    sidereal = {k: tropical_to_sidereal(v.longitude, ay) for k, v in tropical.items()}
    snap = compute_transit_snapshot(prof.chart, sidereal, dt)
    typer.echo(render_transit(snap.highlights))
    for pos in snap.positions:
        typer.echo(f"{pos.planet_name}: {pos.sign} | H(Lagna)={pos.house_from_lagna} | H(Moon)={pos.house_from_moon}")


@app.command("match")
def match(profile: str = typer.Option(..., "--profile"), with_profile: str = typer.Option(..., "--with")) -> None:
    """Calculate Ashta Kuta compatibility between two profiles."""
    store = ProfileStore(get_settings().profile_store)
    a = store.get_by_name(profile)
    b = store.get_by_name(with_profile)
    if a.chart is None:
        a.chart = _build_chart(a.name, a.birth_details)
        store.upsert(a)
    if b.chart is None:
        b.chart = _build_chart(b.name, b.birth_details)
        store.upsert(b)
    result = compute_ashta_kuta(a.chart, b.chart)
    typer.echo(render_compatibility(result))
    typer.echo(json.dumps(result.per_kuta_scores, indent=2))


@app.command("chat")
def chat() -> None:
    """Interactive chat loop with rule-based intent parsing."""
    settings = get_settings()
    store = ProfileStore(settings.profile_store)
    persona = _load_persona_prompt(settings.persona_prompt_file)
    llm = GPT4AllClient(settings.gpt4all_model_name, str(settings.gpt4all_model_path))
    disclaimer_sent: set[str] = set()

    typer.echo("Astro chat ready. Type 'exit' to stop.")
    while True:
        question = typer.prompt("you")
        if question.strip().lower() in {"exit", "quit"}:
            break
        lower = question.lower()
        response = "Please mention a command-style request with profile name."

        if "current dasha" in lower and "profile:" in lower:
            name = question.split("profile:")[-1].strip()
            p = store.get_by_name(name)
            if p.chart is None:
                p.chart = _build_chart(p.name, p.birth_details)
                store.upsert(p)
            moon_lon = next(x.sidereal_longitude for x in p.chart.planet_positions if x.planet_name == "Moon")
            lord = dasha_lord_from_moon_nakshatra(int(moon_lon // 13.3333333333))
            periods = build_vimshottari_periods(lord, to_utc_datetime(str(p.birth_details.date_of_birth), p.birth_details.time_of_birth.isoformat(), p.birth_details.timezone))
            maha, antar, pratyantar = current_dasha_levels(periods, datetime.now(timezone.utc))
            response = render_dasha_now(
                maha.lord if maha else "Unknown",
                antar.lord if antar else None,
                pratyantar.lord if pratyantar else None,
            )
        elif "life overview" in lower and "profile:" in lower:
            name = question.split("profile:")[-1].strip()
            p = store.get_by_name(name)
            if p.chart is None:
                p.chart = _build_chart(p.name, p.birth_details)
                store.upsert(p)
            yogas = detect_yogas(p.chart, load_yoga_rules(settings.vedic_yogas_csv))
            response = render_chart_summary(p.name, p.chart.lagna_sign, p.chart.moon_sign, yogas)
        elif "compare" in lower and "profile" in lower:
            # pattern: compare ... profile A ... profile B
            names = [segment.strip(" .") for segment in question.split("profile") if ":" in segment]
            if len(names) >= 2:
                a_name = names[0].split(":")[-1].strip()
                b_name = names[1].split(":")[-1].strip()
                a = store.get_by_name(a_name)
                b = store.get_by_name(b_name)
                if a.chart is None:
                    a.chart = _build_chart(a.name, a.birth_details)
                    store.upsert(a)
                if b.chart is None:
                    b.chart = _build_chart(b.name, b.birth_details)
                    store.upsert(b)
                response = render_compatibility(compute_ashta_kuta(a.chart, b.chart))

        if llm.available:
            try:
                response = llm.generate_response(persona, [{"role": "user", "content": f"Question: {question}\nAnalysis: {response}"}])
            except Exception as exc:
                LOGGER.warning("LLM generation failed, template response used: %s", exc)

        if "profile:" in lower:
            profile_name = question.split("profile:")[-1].strip()
            if profile_name not in disclaimer_sent:
                typer.echo("Disclaimer: This is guidance and reflection, not medical, psychological, or financial advice.")
                disclaimer_sent.add(profile_name)
        typer.echo(f"astro> {response}")


@app.command("schema")
def schema(out_dir: str = typer.Option("raajeeb_astro_prime/schemas", "--out-dir")) -> None:
    """Export JSON schemas for core models."""
    from raajeeb_astro_prime.models.astro_core import Chart, DashaPeriod, TransitSnapshot
    from raajeeb_astro_prime.models.compatibility import CompatibilityResult

    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)
    files = {
        "Chart.schema.json": Chart.model_json_schema(),
        "DashaPeriod.schema.json": DashaPeriod.model_json_schema(),
        "TransitSnapshot.schema.json": TransitSnapshot.model_json_schema(),
        "CompatibilityResult.schema.json": CompatibilityResult.model_json_schema(),
    }
    for name, payload in files.items():
        (target / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    typer.echo(f"Wrote {len(files)} schema files to {target}")
