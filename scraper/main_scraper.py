import os
import time
import requests
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
YC_BASE_URL = "https://www.ycombinator.com/companies"

def get_db_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not set")
    return psycopg2.connect(DATABASE_URL)

def fetch_companies_page(page):
    # Adjust params if YC uses different pagination (cursor, etc.)
    params = {"page": page}
    resp = requests.get(YC_BASE_URL, params=params, timeout=20)
    resp.raise_for_status()
    return resp.text

def parse_companies(html):
    # just return empty list; next wire BeautifulSoup
    # DB upsert 
    return []

def upsert_company(cur, yc_company_id, name, domain=None, founded_year=None):
    cur.execute(
        """
        INSERT INTO companies (yc_company_id, name, domain, founded_year)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (yc_company_id)
        DO UPDATE SET
            name = EXCLUDED.name,
            domain = EXCLUDED.domain,
            founded_year = EXCLUDED.founded_year,
            last_seen_at = NOW(),
            is_active = TRUE;
        """,
        (yc_company_id, name, domain, founded_year),
    )

def main():
    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    start = time.time()
    total = 0

    # For now just hit page 1 to confirm end-to-end
    html = fetch_companies_page(page=1)
    companies = parse_companies(html)

    for c in companies:
        upsert_company(
            cur,
            yc_company_id=c["yc_company_id"],
            name=c["name"],
            domain=c.get("domain"),
            founded_year=c.get("founded_year"),
        )
        total += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"Inserted/updated {total} companies in {time.time() - start:.2f}s")

if __name__ == "__main__":
    main()
