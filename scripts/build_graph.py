from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPANIES_DIR = ROOT / "data" / "companies"
OUTPUT = ROOT / "docs" / "graph-data.json"

_RADIUS_MAP = {
    "1-10": 5,
    "11-50": 7,
    "51-200": 9,
    "201-500": 11,
    "501-1000": 13,
    "1001-5000": 15,
    "5000+": 18,
}


def load_companies() -> list[dict]:
    """Load all company JSON files from data/companies/."""
    companies = []
    for path in sorted(COMPANIES_DIR.glob("*.json")):
        with path.open() as f:
            companies.append(json.load(f))
    return companies


def extract_nodes(companies: list[dict]) -> list[dict]:
    """Extract graph nodes from company records."""
    nodes = []
    for c in companies:
        ra = c.get("risk_assessment") or {}
        cl = c.get("classification") or {}
        fin = c.get("financials") or {}
        hist = c.get("history") or {}
        ov = c.get("overview") or {}
        sz = c.get("size") or {}
        team = c.get("team") or {}
        careers = c.get("careers") or {}
        glass = c.get("glassdoor") or {}
        rec = c.get("recognition") or {}
        meta = c.get("metadata") or {}

        nodes.append(
            {
                # identity
                "id": c["id"],
                "name": c["name"],
                "category": c.get("category", "company"),
                # overview
                "tagline": ov.get("tagline"),
                "website": ov.get("website"),
                "description_long": ov.get("description_long"),
                # classification
                "ai_focus": cl.get("ai_focus") or [],
                "industries_served": cl.get("industries_served") or [],
                "company_type": cl.get("company_type"),
                "business_type": cl.get("business_type"),
                "is_ai_native": cl.get("is_ai_native"),
                # visual
                "radius": _RADIUS_MAP.get(sz.get("employees_range"), 6),
                "employees_range": sz.get("employees_range"),
                # risk
                "overall_risk": ra.get("overall_risk"),
                "agi_displacement": ra.get("agi_displacement"),
                "agi_displacement_rationale": ra.get("agi_displacement_rationale"),
                "market_risk": ra.get("market_risk"),
                "market_risk_rationale": ra.get("market_risk_rationale"),
                "funding_risk": ra.get("funding_risk"),
                "funding_risk_rationale": ra.get("funding_risk_rationale"),
                "overall_risk_rationale": ra.get("overall_risk_rationale"),
                # history
                "founded_year": hist.get("founded_year"),
                "founders": hist.get("founders") or [],
                "origin_story": hist.get("origin_story"),
                "key_milestones": hist.get("key_milestones") or [],
                # offices
                "offices": c.get("offices") or [],
                # financials
                "business_model": fin.get("business_model"),
                "publicly_traded": fin.get("publicly_traded"),
                "parent_company": fin.get("parent_company"),
                "stock_ticker": fin.get("stock_ticker"),
                "funding_total_usd": fin.get("funding_total_usd"),
                "funding_rounds": fin.get("funding_rounds") or [],
                "investors": fin.get("investors") or [],
                # team
                "leadership": team.get("leadership") or [],
                "notable_people": team.get("notable_people") or [],
                # careers
                "hiring_signals": careers.get("hiring_signals"),
                "open_roles_count": careers.get("open_roles_count"),
                "open_roles": careers.get("open_roles") or [],
                "tech_stack": careers.get("tech_stack") or [],
                "careers_url": careers.get("careers_url"),
                # glassdoor
                "glassdoor_rating": glass.get("rating"),
                "glassdoor_reviews": glass.get("review_count"),
                "glassdoor_recommend": glass.get("recommend_pct"),
                "glassdoor_url": glass.get("glassdoor_url"),
                # recognition
                "awards": rec.get("awards") or [],
                "notable_clients": rec.get("notable_clients") or [],
                "customer_count": rec.get("customer_count"),
                "partnerships": rec.get("partnerships") or [],
                # metadata
                "data_quality": meta.get("data_quality"),
                "scraped_at": meta.get("scraped_at"),
                "sources_used": meta.get("sources_used") or [],
                "notes": meta.get("notes"),
            }
        )
    return nodes


def extract_edges(nodes: list[dict]) -> list[dict]:
    """Extract edges between nodes based on shared attributes."""
    edges = []

    for i, a in enumerate(nodes):
        for b in nodes[i + 1 :]:
            # Shared AI focus
            shared_focus = set(a["ai_focus"]) & set(b["ai_focus"])
            if shared_focus:
                edges.append(
                    {
                        "source": a["id"],
                        "target": b["id"],
                        "type": "ai_focus",
                        "weight": len(shared_focus),
                    }
                )

            # Shared investors
            shared_inv = set(a["investors"]) & set(b["investors"])
            if shared_inv:
                edges.append(
                    {
                        "source": a["id"],
                        "target": b["id"],
                        "type": "investor",
                        "weight": len(shared_inv),
                    }
                )

            # Shared industries
            shared_ind = set(a["industries_served"]) & set(b["industries_served"])
            if shared_ind:
                edges.append(
                    {
                        "source": a["id"],
                        "target": b["id"],
                        "type": "industry",
                        "weight": len(shared_ind),
                    }
                )

            # Explicit partnerships (case-insensitive name match)
            a_partners = {p.lower() for p in a["partnerships"]}
            b_partners = {p.lower() for p in b["partnerships"]}
            if b["name"].lower() in a_partners or a["name"].lower() in b_partners:
                edges.append(
                    {
                        "source": a["id"],
                        "target": b["id"],
                        "type": "partnership",
                        "weight": 1,
                    }
                )

    return edges
