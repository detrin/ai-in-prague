"""Scrape StartupJobs.com API for Prague AI/ML companies not yet in our index."""

import json
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "data" / "companies_index.json"

API_BASE = "https://www.startupjobs.com/api/offers"

# Tags and company areas that indicate AI/ML relevance
SEARCH_TAGS = ["ai", "machine-learning", "data-science", "data-engineering"]
COMPANY_AREA_KEYWORDS = {
    "artificial intelligence",
    "machine learning",
    "data science",
    "data",
    "robotics",
    "computer vision",
    "nlp",
    "analytics",
}

# Only Prague
LOCATION = "prague"

# Fields we extract per company (from offer objects)
# The API returns offers, not companies — we deduplicate by company name


def fetch_page(tag, page):
    params = urllib.parse.urlencode(
        {"tag[]": tag, "superLocation[]": LOCATION, "page": page}
    )
    url = f"{API_BASE}?{params}"
    req = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": "ai-in-prague/0.1"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            if isinstance(data, dict):
                return data.get("resultSet", [])
            return data
    except Exception as e:
        print(f"  fetch error: {e}", file=sys.stderr)
        return []


def fetch_all_offers(tag, max_pages=10):
    all_offers = []
    for page in range(1, max_pages + 1):
        data = fetch_page(tag, page)
        if not data:
            break
        all_offers.extend(data)
        if len(data) < 15:  # less than a full page means last page
            break
        time.sleep(0.5)
    return all_offers


def is_ai_relevant(info):
    """Check if a company is AI/ML relevant based on its areas."""
    areas_lower = [a.lower() for a in info.get("areas", [])]
    return any(kw in area for area in areas_lower for kw in COMPANY_AREA_KEYWORDS)


def extract_company(offer):
    """Extract company info from an offer."""
    return {
        "name": offer.get("company", "").strip(),
        "company_type": offer.get("companyType", ""),
        "areas": offer.get("companyAreas", []),
        "logo_url": offer.get("imageUrl", ""),
        "location": offer.get("locations", ""),
        "sample_role": offer.get("name", ""),
    }


def normalize_name(name):
    """Normalize company name for comparison."""
    n = name.lower()
    for suffix in [
        " s.r.o.",
        " s.r.o",
        " a.s.",
        " a.s",
        " inc.",
        " inc",
        " ltd.",
        " ltd",
    ]:
        n = n.replace(suffix, "")
    for word in [",", ".", " solutions", " ai", " technologies"]:
        n = n.replace(word, "")
    return n.strip()


def load_existing_names():
    """Load existing company names from index for dedup."""
    with open(INDEX) as f:
        index = json.load(f)
    return {normalize_name(e["name"]) for e in index}


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Find Prague AI/ML companies on StartupJobs.com"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=5,
        help="max pages per tag (default: 5)",
    )
    parser.add_argument(
        "--add",
        action="store_true",
        help="add new companies to the index",
    )
    args = parser.parse_args()

    existing = load_existing_names()
    print(f"Existing index: {len(existing)} companies")

    # Collect companies across all tags
    companies = {}  # name -> info
    for tag in SEARCH_TAGS:
        print(f"\nFetching tag: {tag}")
        offers = fetch_all_offers(tag, max_pages=args.max_pages)
        print(f"  {len(offers)} offers")
        for offer in offers:
            name = offer.get("company", "").strip()
            if not name:
                continue
            if name not in companies:
                companies[name] = extract_company(offer)

    # Filter to AI-relevant and Prague-based
    ai_companies = {
        name: info for name, info in companies.items() if is_ai_relevant(info)
    }
    print(f"\nTotal unique companies: {len(companies)}")
    print(f"AI-relevant companies: {len(ai_companies)}")

    # Find new ones not in our index
    new_companies = {}
    for name, info in sorted(ai_companies.items()):
        norm = normalize_name(name)
        if norm not in existing:
            new_companies[name] = info

    print(f"New (not in index): {len(new_companies)}")
    print("-" * 60)

    for name, info in sorted(new_companies.items()):
        areas = ", ".join(info["areas"])
        print(f"  {name:30s}  [{info['company_type']:10s}]  {areas}")

    if args.add and new_companies:
        with open(INDEX) as f:
            index = json.load(f)

        added = 0
        for name, info in sorted(new_companies.items()):
            slug = (
                normalize_name(name)
                .replace(" ", "-")
                .replace("á", "a")
                .replace("č", "c")
                .replace("ě", "e")
                .replace("í", "i")
                .replace("ř", "r")
                .replace("š", "s")
                .replace("ú", "u")
                .replace("ý", "y")
                .replace("ž", "z")
            )
            entry = {
                "id": slug,
                "name": name,
                "category": "company",
                "source": "startupjobs",
                "cnaip_url": None,
                "status": "pending",
            }
            index.append(entry)
            added += 1

        index.sort(key=lambda x: x["id"])
        with open(INDEX, "w") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
            f.write("\n")

        print(f"\nAdded {added} companies to index. Total: {len(index)}")
    elif new_companies and not args.add:
        print("\nRun with --add to add these to the index.")


if __name__ == "__main__":
    main()
