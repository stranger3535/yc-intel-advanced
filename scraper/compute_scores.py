import os
import psycopg2
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from collections import defaultdict


load_dotenv()

DB_URL = os.getenv("NEON_DATABASE_URL") or os.getenv("DATABASE_URL")
if not DB_URL:
    raise RuntimeError("DATABASE_URL / NEON_DATABASE_URL not set")

NOW = datetime.now(timezone.utc)

DAYS_30 = NOW - timedelta(days=30)
DAYS_90 = NOW - timedelta(days=90)
DAYS_180 = NOW - timedelta(days=180)
DAYS_365 = NOW - timedelta(days=365)

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


# Main Logic 
def compute_scores():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    ensure_company_scores_schema(cur)
    conn.commit()

    # Fetch all companies
    cur.execute("SELECT id FROM companies ORDER BY id")
    company_ids = [r[0] for r in cur.fetchall()]
    total = len(company_ids)

    print(f"Scoring {total} companies")

    # Fetch all changes once
    cur.execute("""
        SELECT company_id, change_type, detected_at
        FROM company_changes
        WHERE detected_at IS NOT NULL
    """)
    rows = cur.fetchall()

    changes_by_company = defaultdict(list)

    for cid, ctype, ts in rows:
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        changes_by_company[cid].append((ctype, ts))

    print(f"Found change data for {len(changes_by_company)} companies")

    # Scoring Loop
    for idx, company_id in enumerate(company_ids, start=1):

        changes = changes_by_company.get(company_id, [])

        momentum = 0
        stability = 0

        #  Momentum 
        for change_type, detected_at in changes:

            # Recency weighting
            if detected_at >= DAYS_30:
                base = 10
            elif detected_at >= DAYS_90:
                base = 6
            elif detected_at >= DAYS_180:
                base = 3
            elif detected_at >= DAYS_365:
                base = 1
            else:
                base = 0

            # Change type weight
            if change_type == "STAGE_CHANGE":
                momentum += base + 10
            elif change_type == "BATCH_CHANGE":
                momentum += base + 6
            elif change_type == "WEBSITE_CHANGE":
                momentum += base + 4
            elif change_type == "TAG_CHANGE":
                momentum += base + 3
            elif change_type == "DESCRIPTION_CHANGE":
                momentum += base + 2
            elif change_type == "LOCATION_CHANGE":
                momentum += base + 1
            else:
                momentum += base

        # Small baseline to avoid mass zero scores
        if momentum == 0 and changes:
            momentum = 2

        # Stability 
        if not changes:
            stability = 25  # completely unchanged company
        else:
            recent_changes = sum(1 for _, d in changes if d >= DAYS_90)

            if recent_changes == 0:
                stability += 20
            elif recent_changes <= 2:
                stability += 10
            else:
                stability -= 5

            # Penalize excessive churn
            desc_changes = sum(1 for c, _ in changes if c == "DESCRIPTION_CHANGE")
            if desc_changes >= 3:
                stability -= 5

            loc_changes = sum(1 for c, _ in changes if c == "LOCATION_CHANGE")
            if loc_changes >= 2:
                stability -= 5

        # Clamp values
        momentum = max(0, min(momentum, 100))
        stability = max(0, min(stability, 100))

        #  Upsert 
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

        if idx % PROGRESS_EVERY == 0:
            print(f"Processed {idx}/{total}")

        if idx % BATCH_SIZE == 0:
            conn.commit()
            print(f"Committed {idx}/{total}")

    conn.commit()
    cur.close()
    conn.close()

    print("✓ Company scoring completed successfully")

def compute_company_scores(cur=None):
    """
    Adapter for main.py.
    If cursor is not provided, open a new connection.
    """
    compute_scores()

# Entry 
if __name__ == "__main__":
    compute_scores()