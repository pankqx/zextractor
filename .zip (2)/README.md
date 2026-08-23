# Jewellery Store Lead Generator

A small CLI tool that searches Google Maps for jewellery stores in a given
area (taluk, district, city, or state) and exports their **name, address,
and phone number** to a CSV file — built to replace a lost prototype used
for B2B outreach for a rosewood/silver fusion gifting brand.

Optionally, it can call the **Claude API** to draft a short, personalized
opening line for each shop, ready to use on a cold call or WhatsApp message.

## 1. Setup

```bash
git clone <your-repo-url>
cd jewellery-leads-generator
python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and fill in:
- `GOOGLE_MAPS_API_KEY` — from the [Google Cloud Console](https://console.cloud.google.com/).
  Enable **"Places API (New)"** on your project and set up billing (Google gives
  a free monthly credit that comfortably covers moderate use).
- `ANTHROPIC_API_KEY` — only needed if you use `--enrich` (from
  [console.anthropic.com](https://console.anthropic.com/)).

**Never commit your `.env` file** — it's already in `.gitignore`.

## 2. Usage

Basic search:
```bash
python lead_generator.py --area "Hosur, Tamil Nadu" --count 25
```

Custom keyword (default keyword is "jewellery store"):
```bash
python lead_generator.py --area "Mysuru" --keyword "silver jewellery shop" --count 50
```

With Claude-generated pitch lines per shop:
```bash
python lead_generator.py --area "Coimbatore" --count 30 --enrich
```

Custom output filename:
```bash
python lead_generator.py --area "Salem" --count 20 --output salem_leads.csv
```

## 3. Output

A CSV file with columns:

| name | address | phone | website | area_searched | pitch |
|------|---------|-------|---------|----------------|-------|

## 4. Notes / limits

- Google's Places Text Search API returns up to 20 results per page and a
  maximum of ~60 results per distinct query, so for very large lead counts,
  run the tool multiple times with narrower areas (e.g. by taluk instead of
  by district).
- Some listings won't have a phone number on Google Maps — those rows will
  just have an empty `phone` field.
- `--enrich` makes one Claude API call per shop, so it costs a small amount
  and takes longer for big batches.

## 5. Pushing this to GitHub

```bash
git init
git add .
git commit -m "Initial commit: jewellery store lead generator"
git branch -M main
git remote add origin <your-empty-github-repo-url>
git push -u origin main
```

## Roadmap ideas

- Add taluk/district lists for Indian states so you can loop over an entire
  state automatically.
- De-duplicate leads across multiple searches (by phone number).
- Add a `--resume` flag to append to an existing CSV instead of overwriting.
- Swap CSV output for direct write into a Google Sheet.
