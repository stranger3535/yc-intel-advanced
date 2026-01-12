from datetime import datetime, timezone

def start_scrape_run(cur):
    cur.execute("""
        INSERT INTO scrape_runs (started_at)
        VALUES (%s)
        RETURNING id
    """, (datetime.now(timezone.utc),))
    return cur.fetchone()[0]


def finish_scrape_run(
    cur,
    run_id,
    total,
    new,
    updated,
    unchanged,
    failed,
    avg_ms
):
    cur.execute("""
        UPDATE scrape_runs
        SET
            ended_at = %s,
            total_companies = %s,
            new_companies = %s,
            updated_companies = %s,
            unchanged_companies = %s,
            failed_companies = %s,
            avg_time_per_company_ms = %s
        WHERE id = %s
    """, (
        datetime.now(timezone.utc),
        total,
        new,
        updated,
        unchanged,
        failed,
        avg_ms,
        run_id
    ))
