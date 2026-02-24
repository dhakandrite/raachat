# Raajeeb AstroAlchemy Prime 2.0 (Astro Logic Prime)

A fully local, offline-first Vedic astrology assistant for Windows 10/11. It uses a deterministic Jyotish engine with sidereal Lahiri ayanamsa and whole-sign houses, and can optionally use GPT4All for local natural-language phrasing.

## Offline Design
- No HTTP/API calls at runtime.
- Local profile storage (`profiles.json`).
- Ephemeris backend: `pyswisseph` when available, otherwise local CSV fallback.
- GPT4All optional; app works in template-only mode if missing.

## Windows Setup
1. Install Python 3.10+.
2. Open PowerShell/CMD in this project folder.
3. Create venv:
   ```powershell
   python -m venv venv
   ```
4. Activate:
   ```powershell
   venv\Scripts\activate
   ```
5. Install base dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
6. (Optional) Install local LLM + Swiss Ephemeris extras:
   ```powershell
   pip install -r requirements-optional.txt
   ```
7. Run:
   ```powershell
   python -m raajeeb_astro_prime.main --help
   ```
   or double-click `run_astro_prime.bat`.


## Best Offline LLM Option (Recommended)
If you have multiple local AI platforms (Ollama, LM Studio, VS Code extensions), the **best option for this project right now is GPT4All or template mode** because this app is designed as an offline local CLI and does not require a background server.

- `llm_mode = "auto"` (default): try GPT4All, fallback to template mode.
- `llm_mode = "gpt4all"`: force GPT4All (falls back with warning if unavailable).
- `llm_mode = "template"`: fully deterministic text generation with no model dependency.

You can set this in `raajeeb_astro_prime/config/settings.py` under `AppSettings.llm_mode`.

## Deploy / Runbook (Local Offline)
For a predictable local deployment, run:
```powershell
python -m raajeeb_astro_prime.main health
```
This reports profile-store path, CSV ephemeris availability, Swiss Ephemeris availability, and whether GPT4All is available or template-only mode is active.

## Swiss Ephemeris Note
If using `pyswisseph`, place Swiss ephemeris data files in the expected local path for your environment if needed. Otherwise CSV fallback in `raajeeb_astro_prime/data/ephemeris.csv` is used.

## CLI Commands
```bash
astro health
astro profile create
astro profile list
astro chart summary --profile "Name"
astro chart placements --profile "Name"
astro dasha timeline --profile "Name" --from 2020-01-01 --to 2040-01-01
astro dasha now --profile "Name" --on 2026-02-23
astro transit --profile "Name" --date 2026-02-23
astro match --profile "PersonA" --with "PersonB"
astro chat
astro schema --out-dir raajeeb_astro_prime/schemas
```

## Ethics Disclaimer
Readings are reflective guidance only, not medical, psychological, legal, or financial advice.
