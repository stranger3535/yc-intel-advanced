import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

FIELDS = ["batch", "stage", "location", "description"]

def detect_changes():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    cur.execute("""
        SELECT company_id
        FROM company_snapshots
        GROUP BY company_id
        HAVING COUNT(*) >= 2
    """)
    company_ids = [r[0] for r in cur.fetchall()]

    print(f"Checking {len(company_ids)} companies for changes")

    for company_id in company_ids:
        cur.execute("""
            SELECT batch, stage, location, description, tags
            FROM company_snapshots
            WHERE company_id = %s
            ORDER BY scraped_at DESC
            LIMIT 2
        """, (company_id,))

        latest, previous = cur.fetchall()

        for idx, field in enumerate(FIELDS):
            old = previous[idx]
            new = latest[idx]

            if old != new:
                cur.execute("""
                    INSERT INTO company_changes
                    (company_id, change_type, old_value, new_value)
                    VALUES (%s, %s, %s, %s)
                """, (
                    company_id,
                    f"{field.upper()}_CHANGE",
                    str(old),
                    str(new)
                ))

    conn.commit()
    cur.close()
    conn.close()

    print("✓ Change detection completed")
    
def detect_and_store_changes(cur, snapshot):
    """
    Adapter for main.py.
    For now, reuse detect_changes logic later.
    """
    # TEMP: do nothing, return "unchanged"
    return "unchanged"

if __name__ == "__main__":
    detect_changes()
