import sys
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from db import get_db

load_dotenv()


def export_data():
   
    db_gen = get_db()
    db = next(db_gen) if hasattr(db_gen, "__next__") else db_gen
    cur = db.cursor()

    cur.execute("""
        SELECT
            c.name,
            c.domain,
            cs.location,
            cs.tags,
            cs.description,
            COALESCE(sc.momentum_score, 0)
        FROM companies c
        JOIN company_snapshots cs ON cs.company_id = c.id
        LEFT JOIN company_scores sc ON sc.company_id = c.id
        WHERE
            cs.description IS NOT NULL
            AND cs.description <> ''
            AND cs.tags IS NOT NULL
        LIMIT 500
    """)

    rows = cur.fetchall()

    output_path = os.path.join(BASE_DIR, "backend", "llm_dataset.txt")

    with open(output_path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(
                f"Company Name: {r[0]}\n"
                f"Domain: {r[1]}\n"
                f"Location: {r[2]}\n"
                f"Tags: {r[3]}\n"
                f"Description: {r[4]}\n"
                f"Momentum Score: {r[5]}\n"
                f"---\n"
            )

    cur.close()
    db.close()

    print(f"✅ Clean dataset created at: {output_path}")


if __name__ == "__main__":
    export_data()
