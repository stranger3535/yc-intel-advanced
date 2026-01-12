import time
import logging

from scraper.db import (
    get_conn,
    start_scrape_run,
    finish_scrape_run
)

from scraper.list_scraper import scrape_company_list
from scraper.html_detail_scraper import scrape_company_detail
from scraper.detect_changes import detect_and_store_changes
from scraper.compute_scores import compute_company_scores


logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


def run_scraper():
    conn = get_conn()
    cur = conn.cursor()

    start_time = time.perf_counter()

    run_id = start_scrape_run(cur)
    conn.commit()

    total = 0
    new = 0
    updated = 0
    unchanged = 0
    failed = 0
    timings = []

    try:
        companies = scrape_company_list()

        for company in companies:
            total += 1
            t0 = time.perf_counter()

            try:
                snapshot = scrape_company_detail(company)
                changed = detect_and_store_changes(cur, snapshot)

                if changed == "new":
                    new += 1
                elif changed == "updated":
                    updated += 1
                else:
                    unchanged += 1

            except Exception as e:
                failed += 1
                logging.exception(f"Failed company {company}")
                continue

            timings.append((time.perf_counter() - t0) * 1000)

        compute_company_scores(cur)

        avg_ms = sum(timings) / len(timings) if timings else 0

    finally:
        finish_scrape_run(
            cur,
            run_id,
            total,
            new,
            updated,
            unchanged,
            failed,
            avg_ms
        )
        conn.commit()
        conn.close()

        total_time = time.perf_counter() - start_time
        logging.info(f"Scrape finished in {total_time:.2f}s")


if __name__ == "__main__":
    run_scraper()
