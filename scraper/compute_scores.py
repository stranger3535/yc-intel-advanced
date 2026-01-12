import os
import psycopg2
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from collections import defaultdict

# -------------------- Setup --------------------
load_dotenv()

DB_URL = os.getenv("NEON_DATABASE_URL") or os.getenv("DATABASE_URL")
if not DB_URL:
    raise RuntimeError("DATABASE_URL / NEON_DATABASE_URL not set")

NOW = datetime.now(timezone.utc)
DAYS_90 = NOW - timedelta(days=90)
DAYS_180 = NOW - timedelta(days=180)

BATCH_SIZE = 500
PROGRESS_EVERY = 100


def ensure_company_scores_schema(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS company_scores (
            company_id INTEGER PRIMARY KEY
                REFERENCES companies(id) ON DELETE CASCADE,
            momentum_score INTEGER NOT NULL DEFAULT 0,
            stability_score INTEGER NOT NULL DEFAULT 0,
            last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """)


# -------------------- Main Logic --------------------
def compute_scores():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    ensure_company_scores_schema(cur)
    conn.commit()

    # Fetch all companies FIRST
    cur.execute("SELECT id FROM companies ORDER BY id")
    all_company_ids = [r[0] for r in cur.fetchall()]
    total_companies = len(all_company_ids)

    print(f"Total companies to score: {total_companies}")

    # Fetch all changes ONCE
    print("Fetching all changes in one query...")
    cur.execute("""
        SELECT company_id, change_type, detected_at
        FROM company_changes
    """)
    rows = cur.fetchall()

    changes_by_company = defaultdict(list)

    for company_id, change_type, detected_at in rows:
        if detected_at is None:
            continue
        if detected_at.tzinfo is None:
            detected_at = detected_at.replace(tzinfo=timezone.utc)
        changes_by_company[company_id].append((change_type, detected_at))

    print(f"Found changes for {len(changes_by_company)} companies")
    print("Starting scoring loop...\n")

    processed = 0

    # -------------------- Scoring Loop --------------------
    for idx, company_id in enumerate(all_company_ids, start=1):
        momentum = 0
        stability = 0
        changes = changes_by_company.get(company_id, [])

        # ---------- Momentum ----------
        for change_type, detected_at in changes:
            if detected_at >= DAYS_90:
                momentum += 5
                if change_type == "STAGE_CHANGE":
                    momentum += 10
                elif change_type == "BATCH_CHANGE":
                    momentum += 3

        # ---------- Stability ----------
        if not any(d >= DAYS_180 for _, d in changes):
            stability += 20

        if changes and all(c[0] == "LOCATION_CHANGE" for c in changes):
            stability += 10

        desc_changes = sum(
            1 for c in changes if c[0] == "DESCRIPTION_CHANGE"
        )
        if desc_changes >= 3:
            stability -= 10

        # ---------- Upsert ----------
        cur.execute("""
            INSERT INTO company_scores
                (company_id, momentum_score, stability_score, last_updated)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (company_id)
            DO UPDATE SET
                momentum_score = EXCLUDED.momentum_score,
                stability_score = EXCLUDED.stability_score,
                last_updated = EXCLUDED.last_updated
        """, (company_id, momentum, stability, NOW))

        processed += 1

        # Progress logs
        if idx % PROGRESS_EVERY == 0:
            print(f"Processing {idx}/{total_companies}...")

        if processed % BATCH_SIZE == 0:
            conn.commit()
            print(f"Committed {processed}/{total_companies}")

    conn.commit()
    cur.close()
    conn.close()

    print(f"\n✓ Company scoring completed successfully for {total_companies} companies")


# -------------------- Entry --------------------
if __name__ == "__main__":
    compute_scores()
