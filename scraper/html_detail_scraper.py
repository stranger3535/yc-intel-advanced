import os
import time
import json
import hashlib
import logging
from datetime import datetime

import psycopg2
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# -----------------------------
# Config & Logging
# -----------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("scraper.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# -----------------------------
# Helpers
# -----------------------------

def compute_snapshot_hash(data: dict) -> str:
    payload = json.dumps(
        {
            **data,
            "tags": sorted(data.get("tags") or [])
        },
        sort_keys=True,
        ensure_ascii=False
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# -----------------------------
# DB helpers
# -----------------------------

def get_db_conn():
    return psycopg2.connect(DATABASE_URL)


def get_companies(limit=None):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, yc_company_id
        FROM companies
        WHERE is_active = TRUE
        ORDER BY id
        %s
    """ % (f"LIMIT {limit}" if limit else ""))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [{"id": r[0], "slug": r[1]} for r in rows]


def get_latest_snapshot_hash(cur, company_id):
    cur.execute("""
        SELECT snapshot_hash
        FROM company_snapshots
        WHERE company_id = %s
        ORDER BY scraped_at DESC
        LIMIT 1
    """, (company_id,))
    row = cur.fetchone()
    return row[0] if row else None


# -----------------------------
# Playwright scraper
# -----------------------------

def scrape_company_page(page, slug):
    url = f"https://www.ycombinator.com/companies/{slug}"
    logger.info(f"Opening {url}")

    page.goto(url, timeout=60000)
    page.wait_for_load_state("networkidle")
    time.sleep(1.5)

    def text(selector):
        el = page.query_selector(selector)
        return el.inner_text().strip() if el else None

    name = text("h1")

    description = text("div[class*='prose']")

    def labeled_value(label):
        el = page.query_selector(f"text={label}")
        if not el:
            return None
        parent = el.evaluate_handle("e => e.parentElement")
        value_el = parent.evaluate_handle(
            "p => p.querySelector('span:last-child, div:last-child')"
        )
        return value_el.inner_text().strip() if value_el else None

    batch = labeled_value("Batch")
    stage = labeled_value("Status")
    location = labeled_value("Location")

    tags = [
        el.inner_text().strip()
        for el in page.query_selector_all("a[href*='companies?tag']")
    ]

    return {
        "batch": batch,
        "stage": stage,
        "description": description,
        "location": location,
        "tags": tags,
        "employee_range": None
    }


# -----------------------------
# Main runner
# -----------------------------

def run(limit=10):
    start_time = time.time()

    companies = get_companies(limit)
    logger.info(f"Processing {len(companies)} companies")

    conn = get_db_conn()
    cur = conn.cursor()

    # scrape_runs start
    cur.execute(
        "INSERT INTO scrape_runs (started_at) VALUES (NOW()) RETURNING id"
    )
    scrape_run_id = cur.fetchone()[0]
    conn.commit()

    new_snapshots = unchanged = failed = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for idx, company in enumerate(companies, 1):
            try:
                logger.info(f"[{idx}/{len(companies)}] {company['slug']}")

                data = scrape_company_page(page, company["slug"])
                snapshot_hash = compute_snapshot_hash(data)
                latest_hash = get_latest_snapshot_hash(cur, company["id"])

                if latest_hash == snapshot_hash:
                    unchanged += 1
                    continue

                cur.execute("""
                    INSERT INTO company_snapshots
                    (company_id, batch, stage, description, location,
                     tags, employee_range, scraped_at, snapshot_hash)
                    VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s,NOW(),%s)
                """, (
                    company["id"],
                    data["batch"],
                    data["stage"],
                    data["description"],
                    data["location"],
                    json.dumps(data["tags"]),
                    data["employee_range"],
                    snapshot_hash
                ))

                conn.commit()
                new_snapshots += 1

            except Exception:
                conn.rollback()
                failed += 1
                logger.exception(f"Failed {company['slug']}")

            time.sleep(0.4)

        browser.close()

    elapsed = time.time() - start_time
    avg_ms = (elapsed / max(len(companies), 1)) * 1000

    cur.execute("""
        UPDATE scrape_runs
        SET ended_at = NOW(),
            total_companies = %s,
            new_companies = %s,
            unchanged_companies = %s,
            failed_companies = %s,
            avg_time_per_company_ms = %s
        WHERE id = %s
    """, (
        len(companies),
        new_snapshots,
        unchanged,
        failed,
        avg_ms,
        scrape_run_id
    ))
    conn.commit()

    cur.close()
    conn.close()

    logger.info("HTML detail scraping completed")
    logger.info(f"New snapshots: {new_snapshots}")
    logger.info(f"Unchanged: {unchanged}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Runtime: {elapsed:.2f}s")


if __name__ == "__main__":
    run(limit=10)   # increase gradually → run()
