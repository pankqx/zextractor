#!/usr/bin/env python3
"""
Jewellery Store Lead Generator
------------------------------
Searches Google Maps (via the Google Places API) for jewellery stores in a
given area (taluk/district/city/state) and exports their name, address, and
phone number to a CSV file. Optionally uses the Anthropic Claude API to
generate a short, personalized outreach pitch for each shop.

Usage:
    python lead_generator.py --area "Hosur, Tamil Nadu" --count 25
    python lead_generator.py --area "Mysuru" --keyword "silver jewellery shop" --count 50 --enrich
    python lead_generator.py --area "Coimbatore" --count 30 --output coimbatore_leads.csv

Environment variables (put these in a .env file, see .env.example):
    GOOGLE_MAPS_API_KEY   - required
    ANTHROPIC_API_KEY     - required only if you pass --enrich
"""

import os
import sys
import csv
import time
import argparse
from typing import List, Dict, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

PLACES_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
PLACES_FIELD_MASK = (
    "places.displayName,places.formattedAddress,places.nationalPhoneNumber,"
    "places.internationalPhoneNumber,places.id,places.websiteUri"
)


def search_places(query: str, count: int, api_key: str) -> List[Dict]:
    """
    Search Google Places (Text Search - New) for a query like
    "jewellery store in Hosur, Tamil Nadu" and page through results
    until `count` results are collected (Google returns up to 20 per page,
    max 60 total per query via pagination).
    """
    results: List[Dict] = []
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": PLACES_FIELD_MASK + ",nextPageToken",
    }
    body = {"textQuery": query, "pageSize": min(20, max(1, count))}
    page_token = None

    while len(results) < count:
        if page_token:
            body = {"textQuery": query, "pageToken": page_token}
            # Google requires a short delay before a page token becomes valid
            time.sleep(2)

        resp = requests.post(PLACES_SEARCH_URL, headers=headers, json=body, timeout=30)
        if resp.status_code != 200:
            print(f"  [!] API error {resp.status_code}: {resp.text[:300]}", file=sys.stderr)
            break

        data = resp.json()
        places = data.get("places", [])
        results.extend(places)

        page_token = data.get("nextPageToken")
        if not page_token or not places:
            break

    return results[:count]


def normalize_place(place: Dict, area: str) -> Dict:
    name = place.get("displayName", {}).get("text", "")
    return {
        "name": name,
        "address": place.get("formattedAddress", ""),
        "phone": place.get("nationalPhoneNumber") or place.get("internationalPhoneNumber") or "",
        "website": place.get("websiteUri", ""),
        "area_searched": area,
        "pitch": "",
    }


def generate_pitch(shop_name: str, address: str, api_key: str) -> str:
    """Use Claude to draft a one- or two-line personalized outreach line for a cold call/WhatsApp message."""
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        prompt = (
            f"Write a warm, brief (2 sentences max) opening line for a phone call to a jewellery "
            f"shop called '{shop_name}' located at '{address}'. We are House of Anaika, a Bengaluru "
            f"brand making rosewood and silver fusion gifting and ritual products, and we want to "
            f"introduce our catalogue for potential stocking/B2B partnership. Keep it natural, "
            f"not salesy, and specific to a jewellery retailer."
        )
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip()
    except Exception as e:
        print(f"  [!] Pitch generation failed for {shop_name}: {e}", file=sys.stderr)
        return ""


def save_to_csv(leads: List[Dict], output_path: str):
    if not leads:
        print("No leads to save.")
        return
    fieldnames = ["name", "address", "phone", "website", "area_searched", "pitch"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for lead in leads:
            writer.writerow(lead)
    print(f"Saved {len(leads)} leads to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate jewellery store leads from Google Maps.")
    parser.add_argument("--area", required=True, help="Taluk, district, city, or state to search in")
    parser.add_argument("--keyword", default="jewellery store", help="Search keyword (default: 'jewellery store')")
    parser.add_argument("--count", type=int, default=20, help="Number of leads to fetch (default: 20)")
    parser.add_argument("--output", default=None, help="Output CSV filename")
    parser.add_argument("--enrich", action="store_true", help="Generate a personalized pitch line per shop using Claude")
    args = parser.parse_args()

    if not GOOGLE_MAPS_API_KEY:
        print("ERROR: GOOGLE_MAPS_API_KEY not set. Add it to a .env file (see .env.example).", file=sys.stderr)
        sys.exit(1)

    if args.enrich and not ANTHROPIC_API_KEY:
        print("ERROR: --enrich requires ANTHROPIC_API_KEY to be set in .env", file=sys.stderr)
        sys.exit(1)

    query = f"{args.keyword} in {args.area}"
    print(f"Searching: \"{query}\" (target: {args.count} leads)...")

    raw_places = search_places(query, args.count, GOOGLE_MAPS_API_KEY)
    print(f"Found {len(raw_places)} places.")

    leads = [normalize_place(p, args.area) for p in raw_places]

    if args.enrich:
        print("Generating personalized pitch lines with Claude...")
        for lead in leads:
            lead["pitch"] = generate_pitch(lead["name"], lead["address"], ANTHROPIC_API_KEY)
            time.sleep(0.5)

    output_path = args.output or f"leads_{args.area.replace(' ', '_').replace(',', '')}.csv"
    save_to_csv(leads, output_path)


if __name__ == "__main__":
    main()
