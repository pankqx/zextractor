# AGENTS.md

Instructions for AI coding agents working in this repo.
Humans: read [GUIDE.md](GUIDE.md). It explains everything from zero.

## What this project is

zextractor is a single-file **Python 3 command-line tool** (`lead_generator.py`). It searches the
**Google Places API (New) Text Search** for shops (default keyword "jewellery store") in an area,
and writes name, address, phone and website to a CSV. With `--enrich` it calls the **Anthropic
Claude API** once per shop to draft a short outreach line.

## Layout

```
lead_generator.py   the whole program: search_places, normalize_place, generate_pitch, save_to_csv, main
requirements.txt    requests, python-dotenv, anthropic
README.md           usage
.zip, ".zip (2)/"   leftover upload of an older copy of the same files; safe to delete (ask the owner first)
```

## Commands

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp ".zip (2)/.env.example" .env     # then fill in GOOGLE_MAPS_API_KEY (and ANTHROPIC_API_KEY for --enrich)
python lead_generator.py --area "Hosur, Tamil Nadu" --count 25
python lead_generator.py --area "Mysuru" --count 10 --enrich
```

There are no tests. If you add some, use `pytest` and mock `requests.post` so no real API calls happen.

## Conventions

- Keep it a single dependency-light script unless asked to split it.
- Functions are small and pure where possible; only `main()` reads CLI args and env vars.
- Errors from APIs are printed to `stderr` and the run continues (one bad shop must not kill the batch).
- Type hints from `typing` (`List`, `Dict`, `Optional`) are used on every function.

## Rules for agents

- Never commit `.env` or any API key. The root has no `.gitignore` yet: add one with `.env`, `venv/`, `*.csv` before anything else touches secrets.
- Commit as `pankqx <pankqx@gmail.com>`. Do not add `Co-Authored-By` or any AI trailer.
- Places API calls cost money. Use small `--count` values when testing.
- If you change behaviour, update GUIDE.md in the same PR.
