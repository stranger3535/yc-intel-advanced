import requests
import json
from bs4 import BeautifulSoup

BASE_URL = "https://www.ycombinator.com"
START_URL = f"{BASE_URL}/companies"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_company_urls():
    resp = requests.get(START_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    next_data_script = soup.find("script", id="__NEXT_DATA__")
    if not next_data_script:
        raise RuntimeError("__NEXT_DATA__ not found — page structure changed")

    data = json.loads(next_data_script.string)

    # Navigate Next.js props (this is the key part)
    companies = (
        data.get("props", {})
            .get("pageProps", {})
            .get("companies", [])
    )

    urls = []

    for company in companies:
        slug = company.get("slug")
        if slug:
            urls.append(f"{BASE_URL}/companies/{slug}")

    return urls


if __name__ == "__main__":
    urls = fetch_company_urls()
    print(f"\n Total company URLs found: {len(urls)}")

    for u in urls[:5]:
        print(u)
