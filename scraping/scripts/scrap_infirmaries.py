#!/usr/bin/env python3
"""
Scrape all nurses (infirmières) from sante.fr and export to CSV.

Endpoint: POST https://www.sante.fr/solr/request/ajax/
Pages: ~4840 pages of 25 results each (~120,983 total)
"""

import csv
import time
import sys
import requests
from pathlib import Path

URL = "https://www.sante.fr/solr/request/ajax/"
PER_PAGE = 25
OUTPUT_FILE = Path(__file__).parent / "infirmieres.csv"

# Fields to extract: (csv_column_name, json_key, is_array)
FIELDS = [
    ("rpps", "tm_X3b_und_field_rpps", True),
    ("nom", "tm_X3b_und_field_nom", True),
    ("prenom", "tm_X3b_und_field_prenom", True),
    ("profession", "tm_X3b_und_field_profession_name", True),
    ("specialite", "tm_X3b_und_field_specialite_name", True),
    ("telephone", "tm_X3b_und_field_phone_number", True),
    ("adresse", "ss_field_address", False),
    ("rue", "ss_field_street", False),
    ("code_postal", "ss_field_codepostal", False),
    ("ville", "tm_X3b_und_field_ville", True),
    ("departement", "tm_X3b_und_field_department", True),
    ("region", "tm_X3b_und_field_region", True),
    ("latitude", "fts_field_geolocalisation_lat", False),
    ("longitude", "fts_field_geolocalisation_lon", False),
    ("convention", "tm_X3b_und_convention_type", True),
    ("sesam_vitale", "ss_field_sesam_vitale", False),
    ("teleconsultation", "bs_field_apf_teleconsultation", False),
    ("visites_domicile", "bs_field_visites_domicile", False),
]

CSV_COLUMNS = [f[0] for f in FIELDS]


def fetch_page(page: int, session: requests.Session, rand_id: str, max_retries: int = 3) -> dict:
    """Fetch a single page of results."""
    params = {
        "where": "",
        "user_lat": "",
        "user_lon": "",
        "what": "infirmière",
        "index": "health_offer",
        "rand_id": rand_id,
        "page": str(page),
        "etb": "treat",
    }
    for attempt in range(max_retries):
        try:
            resp = session.post(URL, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError) as e:
            if attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                print(f"  Retry {attempt + 1}/{max_retries} for page {page} ({e}), waiting {wait}s...")
                time.sleep(wait)
            else:
                raise


def extract_record(doc: dict) -> dict:
    """Extract a flat dict from a Solr document."""
    row = {}
    for col_name, json_key, is_array in FIELDS:
        val = doc.get(json_key, "")
        if is_array and isinstance(val, list):
            val = val[0] if val else ""
        if isinstance(val, bool):
            val = "oui" if val else "non"
        row[col_name] = val if val is not None else ""
    return row


def main():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://www.sante.fr/recherche/trouver/infirmi%C3%A8re",
    })

    # Use a single fixed rand_id for all pages to ensure stable sort order during pagination
    rand_id = str(int(time.time() * 1000))

    # First request to get total count
    print("Fetching page 1 to get total count...")
    data = fetch_page(1, session, rand_id)
    grouped = data["datas"]["grouped"]["ss_field_custom_group"]
    total = grouped["ngroups"]
    total_pages = (total + PER_PAGE - 1) // PER_PAGE
    print(f"Total nurses: {total:,}")
    print(f"Total pages:  {total_pages:,}")
    print(f"Output file:  {OUTPUT_FILE}")
    print()

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()

        # Process page 1
        groups = grouped["groups"]
        for group in groups:
            doc = group["doclist"]["docs"][0]
            writer.writerow(extract_record(doc))
        count = len(groups)
        print(f"\rPage 1/{total_pages:,} — {count:,} records extracted", end="", flush=True)

        # Process remaining pages
        for page in range(2, total_pages + 1):
            data = fetch_page(page, session, rand_id)
            groups = data["datas"]["grouped"]["ss_field_custom_group"]["groups"]
            for group in groups:
                doc = group["doclist"]["docs"][0]
                writer.writerow(extract_record(doc))
            count += len(groups)

            if page % 10 == 0 or page == total_pages:
                pct = count / total * 100
                print(f"\rPage {page:,}/{total_pages:,} — {count:,}/{total:,} records ({pct:.1f}%)", end="", flush=True)

            # Small delay to be respectful
            time.sleep(0.2)

    print(f"\n\nDone! {count:,} records saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
