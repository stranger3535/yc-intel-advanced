import json
import os
import sys
from dotenv import load_dotenv

# Fix import path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from db import get_db

load_dotenv()

OUTPUT_PATH = os.path.join(BASE_DIR, "finetune_data.jsonl")


def main():
    # --- Get DB connection safely ---
    db_gen = get_db()

    if hasattr(db_gen, "__next__"):
        db = next(db_gen)
    else:
        db = db_gen

    cur = db.cursor()

    # --- Fetch only GOOD quality data ---
    cur.execute("""
        SELECT
            c.name,
            c.domain,
            cs.description,
            cs.tags,
            COALESCE(sc.momentum_score, 0)
        FROM companies c
        JOIN company_snapshots cs ON cs.company_id = c.id
        LEFT JOIN company_scores sc ON sc.company_id = c.id
        WHERE cs.description IS NOT NULL
          AND cs.description <> ''
          AND cs.tags IS NOT NULL
        LIMIT 5000;
    """)

    rows = cur.fetchall()
    print(f"Fetched {len(rows)} rows")

    if not rows:
        print("❌ No valid rows found. Exiting.")
        return

    # --- Write JSONL ---
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for r in rows:
            name, domain, description, tags, momentum = r

            record = {
                "instruction": "Analyze the startup and summarize its business and growth momentum.",
                "input": (
                    f"Company Name: {name}\n"
                    f"Domain: {domain}\n"
                    f"Tags: {tags}\n"
                    f"Description: {description}\n"
                    f"Momentum Score: {momentum}"
                ),
                "output": (
                    f"{name} operates in the {tags} space. "
                    f"It focuses on {description[:200]}... "
                    f"The company shows a momentum score of {momentum}, "
                    f"indicating its recent activity and growth signals."
                )
            }

            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    cur.close()
    db.close()

    print(f"✅ Fine-tuning dataset created at:\n{OUTPUT_PATH}")


if __name__ == "__main__":
    main()
