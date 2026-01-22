import requests
from bs4 import BeautifulSoup
import logging

YC_BASE_URL = "https://www.ycombinator.com/companies"

logger = logging.getLogger(__name__)


def scrape_company_list(page: int = 1):
    """
    Returns:
        [
          { "yc_company_id": "...", "name": "..." },
          ...
        ]
    """
    params = {"page": page}
    resp = requests.get(YC_BASE_URL, params=params, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    companies = []

    for link in soup.find_all("a", href=True):
        href = link["href"]

        if not href.startswith("/companies/"):
            continue

        parts = href.rstrip("/").split("/")
        if len(parts) < 3:
            continue

        yc_company_id = parts[-1]
        name = link.get_text(strip=True)

        if not name:
            name = yc_company_id

        companies.append(
            {
                "yc_company_id": yc_company_id,
                "name": name,
            }
        )

    # Deduplicate
    uniq = {}
    for c in companies:
        uniq[c["yc_company_id"]] = c

    companies = list(uniq.values())
    logger.info(f"Found {len(companies)} companies")

    return companies