import os
import json
import time
import hashlib
import logging
from datetime import datetime

import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# -----------------------------
# Config & Logging
# -----------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("scraper.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

YC_ALL_COMPANIES_URL = "https://yc-oss.github.io/api/companies/all.json"


# -----------------------------
# Utils
# -----------------------------

def safe_text(value):
    if not value:
        return None
    return str(value).encode("utf-8", "ignore").decode("utf-8")


def compute_snapshot_hash(data: dict) -> str:
    normalized = {
        **data,
        "tags": sorted(data.get("tags") or [])
    }
    payload = json.dumps(normalized, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# -----------------------------
# DB Helpers
# -----------------------------

def get_db_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not set")
    return psycopg2.connect(DATABASE_URL)


# -----------------------------
# Seeding Logic
# -----------------------------

def fetch_all_companies():
    logger.info("Fetching all YC companies from YC-OSS API")
    resp = requests.get(YC_ALL_COMPANIES_URL, timeout=30)
    resp.raise_for_status()
    companies = resp.json()
    logger.info(f"Fetched {len(companies)} companies")
    return companies


def upsert_company(cur, company):
    slug = company.get("slug")
    if not slug:
        return None

    name = safe_text(company.get("name") or slug)
    website = company.get("website") or company.get("url")
    founded_year = company.get("year") or company.get("founded_year")

    cur.execute(
        """
        INSERT INTO companies
        (yc_company_id, name, domain, founded_year, first_seen_at, last_seen_at, is_active)
        VALUES (%s, %s, %s, %s, NOW(), NOW(), TRUE)
        ON CONFLICT (yc_company_id)
        DO UPDATE SET
            name = EXCLUDED.name,
            domain = EXCLUDED.domain,
            founded_year = EXCLUDED.founded_year,
            last_seen_at = NOW(),
            is_active = TRUE
        RETURNING id;
        """,
        (slug, name, website, founded_year),
    )
    return cur.fetchone()["id"]


def get_latest_snapshot_hash(cur, company_id):
    cur.execute(
        """
        SELECT snapshot_hash
        FROM company_snapshots
        WHERE company_id = %s
        ORDER BY scraped_at DESC
        LIMIT 1;
        """,
        (company_id,),
    )
    row = cur.fetchone()
    return row["snapshot_hash"] if row else None


def insert_snapshot_if_changed(cur, company_id, company):
    batch = company.get("batch") or company.get("demo_day_batch")
    stage = company.get("status") or "Active"
    description = safe_text(
        company.get("long_description")
        or company.get("one_liner")
        or company.get("description")
    )
    location = safe_text(company.get("all_locations") or company.get("location"))
    tags = company.get("tags") or company.get("all_tags") or []

    team_size = company.get("team_size")
    employee_range = None
    if isinstance(team_size, int):
        if team_size <= 10:
            employee_range = "1-10"
        elif team_size <= 50:
            employee_range = "11-50"
        elif team_size <= 200:
            employee_range = "51-200"
        else:
            employee_range = "200+"

    snapshot_data = {
        "batch": batch,
        "stage": stage,
        "description": description,
        "location": location,
        "tags": tags,
        "employee_range": employee_range,
    }

    snapshot_hash = compute_snapshot_hash(snapshot_data)
    latest_hash = get_latest_snapshot_hash(cur, company_id)

    if latest_hash == snapshot_hash:
        return False

    cur.execute(
        """
        INSERT INTO company_snapshots
        (company_id, batch, stage, description, location, tags, employee_range, scraped_at, snapshot_hash)
        VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, NOW(), %s);
        """,
        (
            company_id,
            snapshot_data["batch"],
            snapshot_data["stage"],
            snapshot_data["description"],
            snapshot_data["location"],
            json.dumps(snapshot_data["tags"]),
            snapshot_data["employee_range"],
            snapshot_hash,
        ),
    )
    return True


def seed_from_yc_api():
    start_time = time.time()
    companies = fetch_all_companies()

    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # scrape_runs start
    cur.execute(
        "INSERT INTO scrape_runs (started_at) VALUES (NOW()) RETURNING id;"
    )
    scrape_run_id = cur.fetchone()["id"]
    conn.commit()

    total = new_snapshots = unchanged = failed = 0

    for idx, company in enumerate(companies, 1):
        try:
            company_id = upsert_company(cur, company)
            if not company_id:
                continue

            changed = insert_snapshot_if_changed(cur, company_id, company)
            new_snapshots += int(changed)
            unchanged += int(not changed)
            total += 1

            if idx % 100 == 0:
                conn.commit()
                logger.info(f"Processed {idx}/{len(companies)}")

        except Exception:
            conn.rollback()
            failed += 1
            logger.exception(f"Error processing company index {idx}")

    conn.commit()

    elapsed = time.time() - start_time
    avg_ms = (elapsed / max(total, 1)) * 1000

    cur.execute(
        """
        UPDATE scrape_runs
        SET ended_at = NOW(),
            total_companies = %s,
            new_companies = %s,
            unchanged_companies = %s,
            failed_companies = %s,
            avg_time_per_company_ms = %s
        WHERE id = %s;
        """,
        (total, new_snapshots, unchanged, failed, avg_ms, scrape_run_id),
    )
    conn.commit()

    cur.close()
    conn.close()

    logger.info("Seeding completed")
    logger.info(f"Total processed: {total}")
    logger.info(f"New snapshots: {new_snapshots}")
    logger.info(f"Unchanged: {unchanged}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Total runtime: {elapsed:.2f}s")


if __name__ == "__main__":
    print("\n=== Seeding YC companies from YC-OSS API ===\n")
    seed_from_yc_api()
    print("\n✓ Seeding complete. Check scraper.log and your DB.\n")
