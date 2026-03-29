from scripts.build_graph import extract_nodes, extract_edges

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


# --- Edge extraction tests ---


def test_extract_edges_shared_ai_focus():
    # alpha has [nlp, automation], beta has [nlp, cv] → 1 shared: nlp
    nodes = extract_nodes([COMPANY_A, COMPANY_B])
    edges = extract_edges(nodes)
    ai_edges = [
        e
        for e in edges
        if e["type"] == "ai_focus" and {e["source"], e["target"]} == {"alpha", "beta"}
    ]
    assert len(ai_edges) == 1
    assert ai_edges[0]["weight"] == 1


def test_extract_edges_shared_investor():
    # both have Credo Ventures
    nodes = extract_nodes([COMPANY_A, COMPANY_B])
    edges = extract_edges(nodes)
    inv_edges = [
        e
        for e in edges
        if e["type"] == "investor" and {e["source"], e["target"]} == {"alpha", "beta"}
    ]
    assert len(inv_edges) == 1
    assert inv_edges[0]["weight"] == 1


def test_extract_edges_shared_industry():
    # alpha has [finance, healthcare], beta has [healthcare, education] → 1 shared: healthcare
    nodes = extract_nodes([COMPANY_A, COMPANY_B])
    edges = extract_edges(nodes)
    ind_edges = [
        e
        for e in edges
        if e["type"] == "industry" and {e["source"], e["target"]} == {"alpha", "beta"}
    ]
    assert len(ind_edges) == 1
    assert ind_edges[0]["weight"] == 1


def test_extract_edges_partnership():
    # beta.partnerships = ["Alpha Corp"] which matches COMPANY_A.name
    nodes = extract_nodes([COMPANY_A, COMPANY_B])
    edges = extract_edges(nodes)
    part_edges = [
        e
        for e in edges
        if e["type"] == "partnership"
        and {e["source"], e["target"]} == {"alpha", "beta"}
    ]
    assert len(part_edges) == 1
    assert part_edges[0]["weight"] == 1


def test_extract_edges_no_self_loops():
    nodes = extract_nodes([COMPANY_A])
    edges = extract_edges(nodes)
    assert all(e["source"] != e["target"] for e in edges)


def test_extract_edges_no_duplicates():
    nodes = extract_nodes([COMPANY_A, COMPANY_B])
    edges = extract_edges(nodes)
    # Each (source, target, type) pair should appear at most once
    seen = set()
    for e in edges:
        key = (min(e["source"], e["target"]), max(e["source"], e["target"]), e["type"])
        assert key not in seen, f"Duplicate edge: {key}"
        seen.add(key)


def test_extract_edges_weight_reflects_overlap():
    # Make company_c with 2 shared ai_focus with company_a
    company_c = {
        **COMPANY_A,
        "id": "gamma",
        "name": "Gamma",
        "classification": {
            **COMPANY_A["classification"],
            "ai_focus": ["nlp", "automation", "cv"],
        },
    }
    nodes = extract_nodes([COMPANY_A, company_c])
    edges = extract_edges(nodes)
    ai_edges = [e for e in edges if e["type"] == "ai_focus"]
    assert ai_edges[0]["weight"] == 2  # both nlp and automation shared
