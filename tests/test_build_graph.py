from scripts.build_graph import extract_nodes

COMPANY_A = {
    "id": "alpha",
    "name": "Alpha Corp",
    "category": "company",
    "scraped_at": "2026-01-01T00:00:00Z",
    "overview": {
        "tagline": "Making AI work",
        "website": "https://alpha.com",
        "description_long": "Alpha builds AI tools for finance.",
    },
    "classification": {
        "ai_focus": ["nlp", "automation"],
        "industries_served": ["finance", "healthcare"],
        "company_type": "startup",
        "business_type": "b2b_saas",
        "is_ai_native": True,
    },
    "size": {"employees_range": "11-50"},
    "risk_assessment": {
        "overall_risk": "low",
        "agi_displacement": "low",
        "agi_displacement_rationale": "Strong moat",
        "market_risk": "medium",
        "market_risk_rationale": "Competitive space",
        "funding_risk": "low",
        "funding_risk_rationale": "Well funded",
        "overall_risk_rationale": "Solid company",
    },
    "financials": {
        "investors": ["Credo Ventures"],
        "funding_total_usd": 5000000,
        "funding_rounds": [
            {
                "date": "2022",
                "type": "Seed",
                "amount_usd": 5000000,
                "lead_investor": "Credo Ventures",
            }
        ],
        "business_model": "subscription_saas",
        "publicly_traded": False,
        "parent_company": None,
        "stock_ticker": None,
        "stock_exchange": None,
    },
    "history": {
        "founded_year": 2020,
        "founders": ["Jan Novak"],
        "origin_story": "Started in a Prague garage.",
        "key_milestones": [{"year": 2020, "event": "Founded"}],
    },
    "team": {
        "leadership": [{"name": "Jan Novak", "role": "CEO", "source": "website"}],
        "notable_people": [],
    },
    "careers": {
        "hiring_signals": "actively_hiring",
        "open_roles_count": 3,
        "open_roles": [
            {"title": "ML Engineer", "department": "engineering", "location": "Prague"}
        ],
        "tech_stack": ["python", "pytorch"],
        "careers_url": "https://alpha.com/jobs",
    },
    "glassdoor": {
        "rating": 4.2,
        "review_count": 15,
        "recommend_pct": 88,
        "glassdoor_url": None,
    },
    "recognition": {
        "awards": ["Best Startup 2023"],
        "notable_clients": ["Bank CZ"],
        "customer_count": 50,
        "partnerships": ["Beta Corp"],
    },
    "offices": [{"city": "Prague", "country": "CZ", "is_hq": True}],
    "metadata": {
        "data_quality": "high",
        "scraped_at": "2026-01-01T00:00:00Z",
        "sources_used": ["company_website"],
        "notes": "Solid data",
    },
}

COMPANY_B = {
    "id": "beta",
    "name": "Beta Corp",
    "category": "research_group",
    "scraped_at": "2026-01-01T00:00:00Z",
    "overview": {
        "tagline": "Research first",
        "website": "https://beta.cz",
        "description_long": "Beta researches NLP in Prague.",
    },
    "classification": {
        "ai_focus": ["nlp", "cv"],
        "industries_served": ["healthcare", "education"],
        "company_type": "research",
        "business_type": "non_profit",
        "is_ai_native": True,
    },
    "size": {"employees_range": "51-200"},
    "risk_assessment": {
        "overall_risk": "medium",
        "agi_displacement": "high",
        "agi_displacement_rationale": "Research may be superseded",
        "market_risk": "low",
        "market_risk_rationale": "Funded by grants",
        "funding_risk": "medium",
        "funding_risk_rationale": "Grant dependent",
        "overall_risk_rationale": "Mixed",
    },
    "financials": {
        "investors": ["Credo Ventures", "EIB"],
        "funding_total_usd": None,
        "funding_rounds": [],
        "business_model": "grant",
        "publicly_traded": False,
        "parent_company": "Czech Technical University",
        "stock_ticker": None,
        "stock_exchange": None,
    },
    "history": {
        "founded_year": 2015,
        "founders": ["Marie Dvorak"],
        "origin_story": "Spun out of CTU.",
        "key_milestones": [],
    },
    "team": {"leadership": [], "notable_people": []},
    "careers": {
        "hiring_signals": "not_hiring",
        "open_roles_count": 0,
        "open_roles": [],
        "tech_stack": ["python", "tensorflow"],
        "careers_url": None,
    },
    "glassdoor": {
        "rating": None,
        "review_count": None,
        "recommend_pct": None,
        "glassdoor_url": None,
    },
    "recognition": {
        "awards": [],
        "notable_clients": [],
        "customer_count": None,
        "partnerships": ["Alpha Corp"],
    },
    "offices": [{"city": "Prague", "country": "CZ", "is_hq": True}],
    "metadata": {
        "data_quality": "medium",
        "scraped_at": "2026-01-01T00:00:00Z",
        "sources_used": ["company_website"],
        "notes": None,
    },
}


# --- Node extraction tests ---


def test_extract_nodes_returns_one_node_per_company():
    nodes = extract_nodes([COMPANY_A, COMPANY_B])
    assert len(nodes) == 2


def test_extract_nodes_id_and_name():
    nodes = extract_nodes([COMPANY_A])
    assert nodes[0]["id"] == "alpha"
    assert nodes[0]["name"] == "Alpha Corp"


def test_extract_nodes_radius_from_employees_range():
    nodes = extract_nodes([COMPANY_A])  # 11-50
    assert nodes[0]["radius"] == 7
    nodes2 = extract_nodes([COMPANY_B])  # 51-200
    assert nodes2[0]["radius"] == 9


def test_extract_nodes_category_preserved():
    nodes = extract_nodes([COMPANY_A, COMPANY_B])
    ids = {n["id"]: n["category"] for n in nodes}
    assert ids["alpha"] == "company"
    assert ids["beta"] == "research_group"


def test_extract_nodes_risk_and_ai_focus():
    nodes = extract_nodes([COMPANY_A])
    assert nodes[0]["overall_risk"] == "low"
    assert "nlp" in nodes[0]["ai_focus"]
    assert "automation" in nodes[0]["ai_focus"]


def test_extract_nodes_all_detail_fields_present():
    """Every node must carry the fields needed by the detail panel."""
    node = extract_nodes([COMPANY_A])[0]
    for field in [
        "id",
        "name",
        "category",
        "tagline",
        "website",
        "description_long",
        "ai_focus",
        "industries_served",
        "company_type",
        "business_type",
        "is_ai_native",
        "radius",
        "overall_risk",
        "founded_year",
        "founders",
        "origin_story",
        "key_milestones",
        "employees_range",
        "offices",
        "business_model",
        "publicly_traded",
        "parent_company",
        "funding_total_usd",
        "funding_rounds",
        "investors",
        "leadership",
        "notable_people",
        "hiring_signals",
        "open_roles_count",
        "open_roles",
        "tech_stack",
        "careers_url",
        "glassdoor_rating",
        "glassdoor_reviews",
        "glassdoor_recommend",
        "glassdoor_url",
        "awards",
        "notable_clients",
        "customer_count",
        "partnerships",
        "agi_displacement",
        "agi_displacement_rationale",
        "market_risk",
        "market_risk_rationale",
        "funding_risk",
        "funding_risk_rationale",
        "overall_risk_rationale",
        "data_quality",
        "scraped_at",
        "sources_used",
        "notes",
    ]:
        assert field in node, f"Missing field: {field}"
