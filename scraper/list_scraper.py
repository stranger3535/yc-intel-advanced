import os
import time
import logging
import requests
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from bs4 import BeautifulSoup 

# Logging
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
YC_BASE_URL = "https://www.ycombinator.com/companies"


def get_db_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not set")
    return psycopg2.connect(DATABASE_URL)


def fetch_companies_page(page: int) -> str:
    params = {"page": page}
    resp = requests.get(YC_BASE_URL, params=params, timeout=20)
    resp.raise_for_status()
    html = resp.text
    logger.info(f"HTML length for page {page}: {len(html)}")
    logger.info(f"HTML preview:\n{html[:500]}")
    return html


def parse_companies(html: str):
    """
    Parse HTML into a list of {'yc_company_id', 'name'}.
    Uses generic link-based heuristics for YC company cards.
    """
    soup = BeautifulSoup(html, "html.parser")
    companies = []

    # All links on the page
    links = soup.find_all("a", href=True)

    for link in links:
        href = link["href"]

        # Look for links to /companies/<slug>
        if not href.startswith("/companies/"):
            continue

        # Ignore non-company utility links if any
        parts = href.rstrip("/").split("/")
        if len(parts) < 3:
            continue

        yc_company_id = parts[-1]

        # Get a name: try link text; if empty/short, look for heading in parent
        name = link.get_text(strip=True)

        if not name or len(name) < 2:
            parent = link.find_parent()
            if parent:
                heading = parent.find(["h2", "h3", "h4"])
                if heading:
                    name = heading.get_text(strip=True)

        if not name:
            name = yc_company_id

        companies.append(
            {
                "yc_company_id": yc_company_id,
                "name": name,
            }
        )

    # Deduplicate by yc_company_id
    uniq = {}
    for c in companies:
        uniq[c["yc_company_id"]] = c
    companies = list(uniq.values())

    logger.info(f"Parsed {len(companies)} companies from page")
    return companies


def upsert_company(cur, yc_company_id: str, name: str):
    cur.execute(
        """
        INSERT INTO companies (yc_company_id, name)
        VALUES (%s, %s)
        ON CONFLICT (yc_company_id)
        DO UPDATE SET
            name = EXCLUDED.name,
            last_seen_at = NOW(),
            is_active = TRUE;
        """,
        (yc_company_id, name),
    )


def main():
    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    start = time.time()
    total = 0
    page = 1

    logger.info("Starting YC list scraper (HTML parser, first page only for now)")

    html = fetch_companies_page(page)
    companies = parse_companies(html)

    for c in companies:
        upsert_company(cur, c["yc_company_id"], c["name"])
        total += 1

    conn.commit()
    cur.close()
    conn.close()

    elapsed = time.time() - start
    logger.info(f"Inserted/updated {total} companies in {elapsed:.2f}s")
    print(f"Inserted/updated {total} companies in {elapsed:.2f}s")


if __name__ == "__main__":
    main()
