#!/usr/bin/env python3
"""Import infirmieres.csv into Supabase infirmary table via direct PostgreSQL connection."""

import csv
import os
import sys

import psycopg2
from psycopg2.extras import execute_values

DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:8F1XVhBDW2kQkmHr@db.roywfsncxupoouzgwmni.supabase.co:5432/postgres",
)
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "infirmieres.csv")
BATCH_SIZE = 500

INSERT_SQL = """
INSERT INTO public.infirmary
  (rpps, nom, prenom, adresse, rue, code_postal, ville, departement, region, position, visites_domicile)
VALUES %s
"""

TEMPLATE = (
    "(%(rpps)s, %(nom)s, %(prenom)s, %(adresse)s, %(rue)s, %(code_postal)s,"
    " %(ville)s, %(departement)s, %(region)s,"
    " CASE WHEN %(lat)s IS NOT NULL AND %(lon)s IS NOT NULL"
    "   THEN ST_SetSRID(ST_MakePoint(%(lon)s::float, %(lat)s::float), 4326)::geography"
    "   ELSE NULL END,"
    " %(visites)s)"
)


def parse_row(row):
    return {
        "rpps": row["rpps"] or None,
        "nom": row["nom"] or None,
        "prenom": row["prenom"] or None,
        "adresse": row["adresse"] or None,
        "rue": row["rue"] or None,
        "code_postal": row["code_postal"] or None,
        "ville": row["ville"] or None,
        "departement": row["departement"] or None,
        "region": row["region"] or None,
        "lat": row["latitude"] or None,
        "lon": row["longitude"] or None,
        "visites": {"oui": True, "non": False}.get(
            (row["visites_domicile"] or "").strip().lower()
        ),
    }


def main():
    if "{password}" in DB_URL:
        print("Set DATABASE_URL env var with your Supabase database password.")
        sys.exit(1)

    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        batch = []
        total = 0

        for row in reader:
            batch.append(parse_row(row))

            if len(batch) >= BATCH_SIZE:
                execute_values(cur, INSERT_SQL, batch, template=TEMPLATE)
                conn.commit()
                total += len(batch)
                print(f"\r  {total} rows inserted...", end="", flush=True)
                batch = []

        if batch:
            execute_values(cur, INSERT_SQL, batch, template=TEMPLATE)
            conn.commit()
            total += len(batch)

    cur.close()
    conn.close()
    print(f"\n  Done. {total} rows inserted.")


if __name__ == "__main__":
    main()
