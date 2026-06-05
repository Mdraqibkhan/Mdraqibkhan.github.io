"""
Google Scholar scraper for Md Raqib Khan's academic portfolio.
Fetches citation counts, h-index, and per-paper stats from Google Scholar
and writes them to scholar.json for the portfolio site to consume.

Usage:
    pip install scholarly
    python scrape_scholar.py

Runs automatically via GitHub Actions (.github/workflows/update_scholar.yml).
"""

import json
import sys
from datetime import datetime, timezone

try:
    from scholarly import scholarly, ProxyGenerator
except ImportError:
    print("ERROR: 'scholarly' not installed. Run: pip install scholarly")
    sys.exit(1)

SCHOLAR_USER_ID = "RdE9ayMAAAAJ"

def fetch_scholar_data(user_id: str) -> dict:
    print(f"[{datetime.now()}] Fetching Google Scholar profile for user: {user_id}")

    # Optional: use free proxies to avoid rate-limiting in CI
    # pg = ProxyGenerator()
    # pg.FreeProxies()
    # scholarly.use_proxy(pg)

    author = scholarly.search_author_id(user_id)
    author = scholarly.fill(author, sections=["basics", "indices", "publications"])

    total_citations = author.get("citedby", 0)
    h_index = author.get("hindex", 0)
    i10_index = author.get("i10index", 0)

    papers = []
    for pub in author.get("publications", []):
        filled = scholarly.fill(pub)
        bib = filled.get("bib", {})
        papers.append({
            "title": bib.get("title", ""),
            "year": bib.get("pub_year", ""),
            "venue": bib.get("venue", "") or bib.get("journal", "") or bib.get("booktitle", ""),
            "citations": filled.get("num_citations", 0),
            "scholar_url": f"https://scholar.google.com/citations?view_op=view_citation&hl=en&user={user_id}&citation_for_view={filled.get('author_pub_id', '')}",
        })

    # Sort by year descending, then citations descending
    papers.sort(key=lambda p: (-(int(p["year"]) if str(p["year"]).isdigit() else 0), -p["citations"]))

    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "citations": total_citations,
        "h_index": h_index,
        "i10_index": i10_index,
        "publications": len(papers),
        "papers": papers,
    }


def main():
    try:
        data = fetch_scholar_data(SCHOLAR_USER_ID)
    except Exception as e:
        print(f"ERROR: Failed to fetch Scholar data: {e}")
        sys.exit(1)

    output_path = "scholar.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[OK] Wrote {output_path}")
    print(f"     Citations : {data['citations']}")
    print(f"     h-index   : {data['h_index']}")
    print(f"     Papers    : {data['publications']}")
    print(f"     Updated   : {data['updated_at']}")


if __name__ == "__main__":
    main()
