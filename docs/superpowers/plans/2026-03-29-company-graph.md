# Company Relationship Graph Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-contained interactive D3 force-directed graph of the Prague AI company catalog, deployable to GitHub Pages.

**Architecture:** A Python script (`scripts/build_graph.py`) reads all company JSONs and writes `docs/graph-data.json`. A standalone HTML file (`docs/graph.html`) loads that JSON via `fetch()` and renders an interactive force-directed graph with a filter panel, hover tooltips, and a scrollable full-profile detail panel. No backend required.

**Tech Stack:** Python 3.11+, D3.js v7 (CDN), pytest, uv

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `scripts/build_graph.py` | Create | Read company JSONs → emit `graph-data.json` |
| `docs/graph-data.json` | Generated | Graph nodes + edges (gitignored at build time, committed for Pages) |
| `docs/graph.html` | Create | D3 app — all JS/CSS inline, fetches `graph-data.json` |
| `tests/test_build_graph.py` | Create | Unit tests for node/edge extraction |
| `pyproject.toml` | Modify | Add `build-graph` script + `pytest` dev dep |
| `.gitignore` | Modify | Add `.superpowers/` |

---

## Task 1: Repo Setup

**Files:**
- Modify: `.gitignore`
- Modify: `pyproject.toml`

- [ ] **Step 1: Add `.superpowers/` to `.gitignore`**

Add after the last line of `.gitignore`:
```
.superpowers/
```

- [ ] **Step 2: Add pytest + build-graph to pyproject.toml**

In `pyproject.toml`, update `[dependency-groups]` and `[project.scripts]`:

```toml
[dependency-groups]
dev = [
    "jupyter>=1.1.1",
    "matplotlib>=3.10.8",
    "pandas>=3.0.1",
    "papermill>=2.7.0",
    "pre-commit>=4.5.1",
    "pytest>=8.0",
    "seaborn>=0.13.2",
]

[project.scripts]
scrape = "scripts.dispatch:main"
validate = "scripts.validate_company:cli"
render = "scripts.render_leaflets:main"
build-graph = "scripts.build_graph:main"
```

- [ ] **Step 3: Install dev deps**

```bash
uv sync --dev
```

Expected: resolves and installs pytest.

- [ ] **Step 4: Ensure `docs/` and `tests/` directories exist**

```bash
mkdir -p docs tests
touch tests/__init__.py
```

- [ ] **Step 5: Commit**

```bash
git add .gitignore pyproject.toml tests/__init__.py
git commit -m "chore: add pytest, build-graph entry point, update gitignore"
```

---

## Task 2: `build_graph.py` — Node Extraction

**Files:**
- Create: `tests/test_build_graph.py`
- Create: `scripts/build_graph.py`

### Fixtures (used in all test tasks)

- [ ] **Step 1: Write fixtures and failing node extraction tests**

Create `tests/test_build_graph.py`:

```python
import pytest
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
        "funding_rounds": [{"date": "2022", "type": "Seed", "amount_usd": 5000000, "lead_investor": "Credo Ventures"}],
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
        "open_roles": [{"title": "ML Engineer", "department": "engineering", "location": "Prague"}],
        "tech_stack": ["python", "pytorch"],
        "careers_url": "https://alpha.com/jobs",
    },
    "glassdoor": {"rating": 4.2, "review_count": 15, "recommend_pct": 88, "glassdoor_url": None},
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
    "glassdoor": {"rating": None, "review_count": None, "recommend_pct": None, "glassdoor_url": None},
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
        "id", "name", "category", "tagline", "website",
        "description_long", "ai_focus", "industries_served",
        "company_type", "business_type", "is_ai_native",
        "radius", "overall_risk", "founded_year", "founders",
        "origin_story", "key_milestones", "employees_range",
        "offices", "business_model", "publicly_traded", "parent_company",
        "funding_total_usd", "funding_rounds", "investors",
        "leadership", "notable_people",
        "hiring_signals", "open_roles_count", "open_roles", "tech_stack", "careers_url",
        "glassdoor_rating", "glassdoor_reviews", "glassdoor_recommend", "glassdoor_url",
        "awards", "notable_clients", "customer_count", "partnerships",
        "agi_displacement", "agi_displacement_rationale",
        "market_risk", "market_risk_rationale",
        "funding_risk", "funding_risk_rationale",
        "overall_risk_rationale",
        "data_quality", "scraped_at", "sources_used", "notes",
    ]:
        assert field in node, f"Missing field: {field}"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_build_graph.py -v 2>&1 | head -20
```

Expected: `ImportError: cannot import name 'extract_nodes' from 'scripts.build_graph'` (file doesn't exist yet).

- [ ] **Step 3: Implement `extract_nodes` in `scripts/build_graph.py`**

Create `scripts/build_graph.py`:

```python
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

        nodes.append({
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
        })
    return nodes
```

- [ ] **Step 4: Run node tests — verify all pass**

```bash
uv run pytest tests/test_build_graph.py -k "node" -v
```

Expected: all 6 node tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/build_graph.py tests/test_build_graph.py
git commit -m "feat: add build_graph node extraction with tests"
```

---

## Task 3: `build_graph.py` — Edge Extraction

**Files:**
- Modify: `tests/test_build_graph.py` (add edge tests)
- Modify: `scripts/build_graph.py` (add `extract_edges`)

- [ ] **Step 1: Add failing edge tests to `tests/test_build_graph.py`**

Append to the file:

```python
# --- Edge extraction tests ---

def test_extract_edges_shared_ai_focus():
    # alpha has [nlp, automation], beta has [nlp, cv] → 1 shared: nlp
    nodes = extract_nodes([COMPANY_A, COMPANY_B])
    edges = extract_edges(nodes)
    ai_edges = [e for e in edges if e["type"] == "ai_focus" and
                {e["source"], e["target"]} == {"alpha", "beta"}]
    assert len(ai_edges) == 1
    assert ai_edges[0]["weight"] == 1


def test_extract_edges_shared_investor():
    # both have Credo Ventures
    nodes = extract_nodes([COMPANY_A, COMPANY_B])
    edges = extract_edges(nodes)
    inv_edges = [e for e in edges if e["type"] == "investor" and
                 {e["source"], e["target"]} == {"alpha", "beta"}]
    assert len(inv_edges) == 1
    assert inv_edges[0]["weight"] == 1


def test_extract_edges_shared_industry():
    # alpha has [finance, healthcare], beta has [healthcare, education] → 1 shared: healthcare
    nodes = extract_nodes([COMPANY_A, COMPANY_B])
    edges = extract_edges(nodes)
    ind_edges = [e for e in edges if e["type"] == "industry" and
                 {e["source"], e["target"]} == {"alpha", "beta"}]
    assert len(ind_edges) == 1
    assert ind_edges[0]["weight"] == 1


def test_extract_edges_partnership():
    # beta.partnerships = ["Alpha Corp"] which matches COMPANY_A.name
    nodes = extract_nodes([COMPANY_A, COMPANY_B])
    edges = extract_edges(nodes)
    part_edges = [e for e in edges if e["type"] == "partnership" and
                  {e["source"], e["target"]} == {"alpha", "beta"}]
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
    company_c = {**COMPANY_A, "id": "gamma", "name": "Gamma",
                 "classification": {**COMPANY_A["classification"], "ai_focus": ["nlp", "automation", "cv"]}}
    nodes = extract_nodes([COMPANY_A, company_c])
    edges = extract_edges(nodes)
    ai_edges = [e for e in edges if e["type"] == "ai_focus"]
    assert ai_edges[0]["weight"] == 2  # both nlp and automation shared
```

- [ ] **Step 2: Run to verify new tests fail**

```bash
uv run pytest tests/test_build_graph.py -k "edge" -v 2>&1 | head -10
```

Expected: `ImportError` or `NameError` for `extract_edges`.

- [ ] **Step 3: Implement `extract_edges` in `scripts/build_graph.py`**

Add after `extract_nodes`:

```python
def extract_edges(nodes: list[dict]) -> list[dict]:
    """Extract edges between nodes based on shared attributes."""
    edges = []
    name_to_id = {n["name"].lower(): n["id"] for n in nodes}

    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            # Shared AI focus
            shared_focus = set(a["ai_focus"]) & set(b["ai_focus"])
            if shared_focus:
                edges.append({
                    "source": a["id"], "target": b["id"],
                    "type": "ai_focus", "weight": len(shared_focus),
                })

            # Shared investors
            shared_inv = set(a["investors"]) & set(b["investors"])
            if shared_inv:
                edges.append({
                    "source": a["id"], "target": b["id"],
                    "type": "investor", "weight": len(shared_inv),
                })

            # Shared industries
            shared_ind = set(a["industries_served"]) & set(b["industries_served"])
            if shared_ind:
                edges.append({
                    "source": a["id"], "target": b["id"],
                    "type": "industry", "weight": len(shared_ind),
                })

            # Explicit partnerships (case-insensitive name match)
            a_partners = {p.lower() for p in a["partnerships"]}
            b_partners = {p.lower() for p in b["partnerships"]}
            if b["name"].lower() in a_partners or a["name"].lower() in b_partners:
                edges.append({
                    "source": a["id"], "target": b["id"],
                    "type": "partnership", "weight": 1,
                })

    return edges
```

- [ ] **Step 4: Run all edge tests — verify they pass**

```bash
uv run pytest tests/test_build_graph.py -k "edge" -v
```

Expected: all 7 edge tests pass.

- [ ] **Step 5: Run full test suite**

```bash
uv run pytest tests/test_build_graph.py -v
```

Expected: all 13 tests pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/build_graph.py tests/test_build_graph.py
git commit -m "feat: add build_graph edge extraction with tests"
```

---

## Task 4: `build_graph.py` — `main()` + Generate Output

**Files:**
- Modify: `scripts/build_graph.py` (add `main`)

- [ ] **Step 1: Add `main()` to `scripts/build_graph.py`**

Append to the file:

```python
def main() -> None:
    """Entry point: read all companies, write docs/graph-data.json."""
    print("Loading companies...")
    companies = load_companies()
    print(f"  {len(companies)} companies loaded")

    nodes = extract_nodes(companies)
    edges = extract_edges(nodes)

    # Stats
    by_type: dict[str, int] = {}
    for e in edges:
        by_type[e["type"]] = by_type.get(e["type"], 0) + 1
    print(f"  {len(nodes)} nodes, {len(edges)} edges")
    for t, count in sorted(by_type.items()):
        print(f"    {t}: {count}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w") as f:
        json.dump({"nodes": nodes, "edges": edges}, f, ensure_ascii=False)
    print(f"Written: {OUTPUT}")
```

- [ ] **Step 2: Run the build command**

```bash
uv run build-graph
```

Expected output (numbers will vary):
```
Loading companies...
  375 companies loaded
  375 nodes, NNNN edges
    ai_focus: NNNN
    industry: NNNN
    investor: NN
    partnership: NN
Written: .../docs/graph-data.json
```

- [ ] **Step 3: Verify output is valid JSON with expected shape**

```bash
python3 -c "
import json
d = json.load(open('docs/graph-data.json'))
print('nodes:', len(d['nodes']))
print('edges:', len(d['edges']))
print('edge types:', set(e['type'] for e in d['edges']))
print('sample node keys:', list(d['nodes'][0].keys())[:10])
"
```

Expected: `nodes: 375`, edge types include all 4 types, node has expected keys.

- [ ] **Step 4: Commit**

```bash
git add scripts/build_graph.py docs/graph-data.json
git commit -m "feat: add build_graph main, generate graph-data.json"
```

---

## Task 5: `docs/graph.html` — Skeleton + Force Simulation

**Files:**
- Create: `docs/graph.html`

- [ ] **Step 1: Create the base HTML file**

Create `docs/graph.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Prague AI Graph</title>
<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0d0d1a; color: #ccc; font-family: system-ui, sans-serif; overflow: hidden; }

  /* Layout */
  #topbar {
    position: fixed; top: 0; left: 0; right: 0; height: 48px;
    background: #111; border-bottom: 1px solid #333;
    display: flex; align-items: center; padding: 0 16px; gap: 12px; z-index: 100;
  }
  #topbar h1 { color: #4fa3e0; font-size: 15px; white-space: nowrap; }
  #search {
    flex: 0 0 220px; padding: 5px 10px; background: #1a1a2e;
    border: 1px solid #333; border-radius: 4px; color: #ccc; font-size: 13px;
  }
  #search:focus { outline: none; border-color: #4fa3e0; }
  #node-count { color: #555; font-size: 12px; margin-left: auto; }

  #left-panel {
    position: fixed; top: 48px; left: 0; width: 220px; bottom: 0;
    background: #111; border-right: 1px solid #333;
    overflow-y: auto; padding: 14px; z-index: 90;
    display: flex; flex-direction: column; gap: 16px;
  }
  #canvas-area {
    position: fixed; top: 48px; left: 220px; right: 0; bottom: 0;
  }
  #canvas-area.panel-open { right: 360px; }
  #graph-svg { width: 100%; height: 100%; }

  #right-panel {
    position: fixed; top: 48px; right: -360px; width: 360px; bottom: 0;
    background: #111; border-left: 1px solid #333;
    overflow-y: auto; z-index: 90;
    transition: right 0.2s ease;
  }
  #right-panel.open { right: 0; }

  /* Filter panel */
  .filter-group { display: flex; flex-direction: column; gap: 6px; }
  .filter-label { color: #666; font-size: 10px; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px; }
  .edge-toggle { display: flex; align-items: center; gap: 7px; font-size: 13px; color: #ccc; cursor: pointer; }
  .edge-toggle input[type=checkbox] { cursor: pointer; }
  .color-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
  .filter-select, .filter-range {
    width: 100%; background: #1a1a2e; border: 1px solid #333; border-radius: 3px;
    color: #ccc; padding: 4px 6px; font-size: 12px;
  }
  .filter-select:focus { outline: none; border-color: #4fa3e0; }
  .range-row { display: flex; justify-content: space-between; color: #555; font-size: 10px; margin-top: 2px; }

  /* Tooltip */
  #tooltip {
    position: fixed; pointer-events: none; background: #1a1a2e;
    border: 1px solid #4fa3e0; border-radius: 4px; padding: 8px 10px;
    font-size: 12px; max-width: 220px; z-index: 200; display: none;
  }
  #tooltip h4 { color: white; margin-bottom: 3px; }
  #tooltip .tip-sub { color: #888; font-size: 11px; margin-bottom: 4px; }
  #tooltip .tip-tags { display: flex; flex-wrap: wrap; gap: 3px; margin-bottom: 4px; }
  #tooltip .tip-tag { background: #1e3a5f; color: #4fa3e0; padding: 1px 5px; border-radius: 2px; font-size: 10px; }
  #tooltip .tip-meta { color: #666; font-size: 10px; }

  /* Detail panel */
  #panel-header {
    position: sticky; top: 0; background: #2563EB; padding: 12px 14px;
    display: flex; align-items: flex-start; justify-content: space-between; gap: 8px;
  }
  #panel-header h2 { color: white; font-size: 16px; margin: 0; }
  #panel-tagline { color: rgba(255,255,255,0.8); font-size: 11px; margin-top: 3px; }
  #panel-close {
    background: none; border: none; color: white; font-size: 18px;
    cursor: pointer; flex-shrink: 0; line-height: 1; padding: 0;
  }
  #panel-body { padding: 12px 14px; display: flex; flex-direction: column; gap: 14px; }
  .panel-section h3 {
    color: #4fa3e0; font-size: 10px; text-transform: uppercase;
    letter-spacing: 0.05em; margin-bottom: 6px;
  }
  .panel-section p, .panel-section li { font-size: 12px; color: #bbb; line-height: 1.55; }
  .tag-row { display: flex; flex-wrap: wrap; gap: 4px; }
  .tag { background: #1e3a5f; color: #4fa3e0; padding: 2px 7px; border-radius: 2px; font-size: 11px; }
  .tag.green { background: #0d2b1a; color: #7ed321; }
  .tag.orange { background: #2b1f0d; color: #f5a623; }
  .kv-table { width: 100%; border-collapse: collapse; font-size: 12px; }
  .kv-table td { padding: 2px 0; vertical-align: top; }
  .kv-table td:first-child { color: #666; width: 40%; }
  .kv-table td:last-child { color: #ccc; }
  .risk-row { display: flex; align-items: flex-start; gap: 8px; margin-bottom: 5px; }
  .risk-badge {
    flex-shrink: 0; padding: 2px 6px; border-radius: 2px;
    font-size: 10px; font-weight: bold; color: white;
  }
  .risk-badge.low { background: #059669; }
  .risk-badge.medium { background: #d97706; }
  .risk-badge.high { background: #dc2626; }
  .risk-badge.not_applicable { background: #6b7280; }
  .risk-rationale { color: #888; font-size: 11px; line-height: 1.45; }
  .conn-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 4px; }
  .panel-footer { border-top: 1px solid #222; padding-top: 10px; display: flex; justify-content: space-between; align-items: center; }
  .panel-footer a { color: #4fa3e0; font-size: 12px; text-decoration: none; }
  .panel-footer span { color: #444; font-size: 10px; }
  hr.panel-divider { border: none; border-top: 1px solid #1e1e2e; }

  /* Graph elements */
  .node circle { cursor: pointer; transition: opacity 0.15s; }
  .node circle:hover { stroke: white !important; }
  .node.dimmed circle { opacity: 0.15; }
  .link { transition: opacity 0.15s; }
  .link.dimmed { opacity: 0.03 !important; }
  .node.highlighted circle { stroke: white !important; stroke-width: 2px !important; }
</style>
</head>
<body>

<!-- Top bar -->
<div id="topbar">
  <h1>Prague AI Graph</h1>
  <input id="search" type="text" placeholder="Search companies...">
  <span id="node-count"></span>
</div>

<!-- Left filter panel -->
<div id="left-panel">
  <div class="filter-group">
    <div class="filter-label">Edge types</div>
    <label class="edge-toggle"><input type="checkbox" id="toggle-ai_focus" checked>
      <span class="color-dot" style="background:#4fa3e0"></span>AI focus</label>
    <label class="edge-toggle"><input type="checkbox" id="toggle-investor" checked>
      <span class="color-dot" style="background:#f5a623"></span>Investors</label>
    <label class="edge-toggle"><input type="checkbox" id="toggle-industry">
      <span class="color-dot" style="background:#7ed321"></span>Industry</label>
    <label class="edge-toggle"><input type="checkbox" id="toggle-partnership" checked>
      <span class="color-dot" style="background:#e05c5c"></span>Partnerships</label>
  </div>

  <div class="filter-group">
    <div class="filter-label">Min shared tags <span id="min-weight-val">2</span></div>
    <input type="range" id="min-weight" class="filter-range" min="1" max="5" value="2">
    <div class="range-row"><span>1</span><span>3</span><span>5</span></div>
  </div>

  <div class="filter-group">
    <div class="filter-label">Color by</div>
    <select id="color-by" class="filter-select">
      <option value="category">Category</option>
      <option value="ai_focus">Primary AI focus</option>
      <option value="company_type">Company type</option>
      <option value="overall_risk">Overall risk</option>
    </select>
  </div>

  <div class="filter-group">
    <div class="filter-label">Show nodes</div>
    <select id="filter-nodes" class="filter-select">
      <option value="all">All</option>
      <option value="company">Companies only</option>
      <option value="research_group">Research groups</option>
      <option value="ai_native">AI-native only</option>
    </select>
  </div>

  <div class="filter-group">
    <div class="filter-label">Cluster gravity <span id="gravity-val">4</span></div>
    <input type="range" id="gravity" class="filter-range" min="0" max="10" value="4">
    <div class="range-row"><span>off</span><span>strong</span></div>
  </div>
</div>

<!-- Graph canvas -->
<div id="canvas-area">
  <svg id="graph-svg"></svg>
</div>

<!-- Tooltip -->
<div id="tooltip"></div>

<!-- Right detail panel -->
<div id="right-panel">
  <div id="panel-header">
    <div>
      <h2 id="panel-name"></h2>
      <div id="panel-tagline"></div>
    </div>
    <button id="panel-close">×</button>
  </div>
  <div id="panel-body"></div>
</div>

<script>
// ── Constants ────────────────────────────────────────────────────────────────
const EDGE_COLORS = {
  ai_focus:    '#4fa3e0',
  investor:    '#f5a623',
  industry:    '#7ed321',
  partnership: '#e05c5c',
};

const CATEGORY_COLORS = { company: '#4fa3e0', research_group: '#e05c5c', initiative: '#f5a623' };

const AI_FOCUS_COLORS = {
  automation: '#4fa3e0', nlp: '#a78bfa', generative_ai: '#f472b6',
  cv: '#34d399', data_engineering: '#fb923c', ml_ops: '#60a5fa',
  recommendation: '#f59e0b', speech: '#4ade80', document_processing: '#e879f9',
  other: '#9ca3af',
};

const RISK_COLORS = { low: '#059669', medium: '#d97706', high: '#dc2626', not_applicable: '#6b7280' };

const COMPANY_TYPE_COLORS = {
  startup: '#60a5fa', scaleup: '#34d399', enterprise: '#f59e0b',
  research: '#a78bfa', sme: '#fb923c', non_profit: '#e879f9',
};

// ── State ────────────────────────────────────────────────────────────────────
let allNodes = [], allEdges = [];
let activeNodes = [], activeEdges = [];
let selectedId = null;
let simulation, svgEl, linkSel, nodeSel, clusterCentroids = {};

// ── Data loading ─────────────────────────────────────────────────────────────
fetch('graph-data.json')
  .then(r => r.json())
  .then(data => {
    allNodes = data.nodes;
    allEdges = data.edges;
    initGraph();
    applyFilters();
    wireControls();
  })
  .catch(err => {
    document.body.innerHTML = `<div style="color:#e05c5c;padding:40px;font-size:14px">
      Failed to load graph-data.json.<br>
      Run: <code>uv run build-graph</code><br>
      Then serve locally: <code>python -m http.server -d docs 8080</code><br>
      Error: ${err.message}
    </div>`;
  });

// ── Graph init ───────────────────────────────────────────────────────────────
function initGraph() {
  const canvas = document.getElementById('canvas-area');
  svgEl = d3.select('#graph-svg');
  svgEl.selectAll('*').remove();

  const zoom = d3.zoom()
    .scaleExtent([0.1, 5])
    .on('zoom', e => g.attr('transform', e.transform));

  svgEl.call(zoom);
  svgEl.on('click', (event) => {
    if (event.target === svgEl.node() || event.target.tagName === 'svg') deselect();
  });

  const g = svgEl.append('g');
  linkSel = g.append('g').attr('class', 'links').selectAll('line');
  nodeSel = g.append('g').attr('class', 'nodes').selectAll('g');

  const W = canvas.offsetWidth, H = canvas.offsetHeight;
  simulation = d3.forceSimulation()
    .force('link', d3.forceLink().id(d => d.id).distance(60).strength(d => 0.1 + d.weight * 0.05))
    .force('charge', d3.forceManyBody().strength(-120))
    .force('center', d3.forceCenter(W / 2, H / 2))
    .force('collide', d3.forceCollide().radius(d => d.radius + 4))
    .on('tick', ticked);
}

// ── Rendering ────────────────────────────────────────────────────────────────
function render() {
  const canvas = document.getElementById('canvas-area');
  const W = canvas.offsetWidth, H = canvas.offsetHeight;

  // Compute cluster centroids (for gravity force)
  clusterCentroids = {};
  const focusCounts = {};
  for (const n of activeNodes) {
    const f = n.ai_focus[0] || 'other';
    if (!clusterCentroids[f]) { clusterCentroids[f] = {x: 0, y: 0, count: 0}; focusCounts[f] = 0; }
    clusterCentroids[f].count++;
  }
  // Arrange cluster targets in a circle
  const clusterKeys = Object.keys(clusterCentroids);
  clusterKeys.forEach((k, i) => {
    const angle = (i / clusterKeys.length) * 2 * Math.PI;
    const r = Math.min(W, H) * 0.28;
    clusterCentroids[k].tx = W / 2 + r * Math.cos(angle);
    clusterCentroids[k].ty = H / 2 + r * Math.sin(angle);
  });

  // Links
  linkSel = linkSel.data(activeEdges, d => `${d.source.id||d.source}-${d.target.id||d.target}-${d.type}`)
    .join('line')
    .attr('class', 'link')
    .attr('stroke', d => EDGE_COLORS[d.type])
    .attr('stroke-opacity', d => {
      if (d.type === 'partnership') return 0.8;
      if (d.type === 'investor') return Math.min(0.8, 0.4 + d.weight * 0.15);
      return Math.min(0.5, 0.2 + d.weight * 0.08);
    })
    .attr('stroke-width', d => d.type === 'partnership' ? 2 : 1)
    .attr('stroke-dasharray', d => d.type === 'industry' ? '4,3' : null);

  // Nodes
  nodeSel = nodeSel.data(activeNodes, d => d.id)
    .join(
      enter => {
        const g = enter.append('g').attr('class', 'node').call(
          d3.drag()
            .on('start', dragStart)
            .on('drag', dragged)
            .on('end', dragEnd)
        );
        g.append('circle');
        return g;
      }
    )
    .on('click', (event, d) => { event.stopPropagation(); selectNode(d.id); })
    .on('mouseover', showTooltip)
    .on('mousemove', moveTooltip)
    .on('mouseout', hideTooltip);

  nodeSel.select('circle')
    .attr('r', d => d.radius)
    .attr('fill', d => nodeColor(d))
    .attr('stroke', d => riskStroke(d).color)
    .attr('stroke-width', d => riskStroke(d).width);

  document.getElementById('node-count').textContent =
    `${activeNodes.length} nodes · ${activeEdges.length} edges`;

  simulation.nodes(activeNodes);
  simulation.force('link').links(activeEdges);
  simulation.alpha(0.6).restart();
}

function ticked() {
  const gravityStrength = +document.getElementById('gravity').value / 200;
  if (gravityStrength > 0) {
    for (const n of activeNodes) {
      const f = n.ai_focus[0] || 'other';
      const c = clusterCentroids[f];
      if (c) {
        n.vx += (c.tx - n.x) * gravityStrength;
        n.vy += (c.ty - n.y) * gravityStrength;
      }
    }
  }

  linkSel
    .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
    .attr('x2', d => d.target.x).attr('y2', d => d.target.y);

  nodeSel.attr('transform', d => `translate(${d.x},${d.y})`);
}

// ── Color helpers ─────────────────────────────────────────────────────────────
function nodeColor(d) {
  const mode = document.getElementById('color-by').value;
  if (mode === 'category') return CATEGORY_COLORS[d.category] || '#9ca3af';
  if (mode === 'ai_focus') return AI_FOCUS_COLORS[d.ai_focus[0]] || '#9ca3af';
  if (mode === 'company_type') return COMPANY_TYPE_COLORS[d.company_type] || '#9ca3af';
  if (mode === 'overall_risk') return RISK_COLORS[d.overall_risk] || '#9ca3af';
  return '#4fa3e0';
}

function riskStroke(d) {
  const w = d.overall_risk === 'high' ? 3.5 : d.overall_risk === 'medium' ? 2 : 1;
  const color = d.overall_risk === 'high' ? '#dc2626' : '#333';
  return { width: w, color };
}

// ── Drag ──────────────────────────────────────────────────────────────────────
function dragStart(event, d) {
  if (!event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x; d.fy = d.y;
}
function dragged(event, d) { d.fx = event.x; d.fy = event.y; }
function dragEnd(event, d) {
  if (!event.active) simulation.alphaTarget(0);
  // Keep pinned — double-click to unpin
}
svgEl && svgEl.selectAll('.node').on('dblclick', (event, d) => { d.fx = null; d.fy = null; });

// ── Tooltip ───────────────────────────────────────────────────────────────────
function showTooltip(event, d) {
  const tip = document.getElementById('tooltip');
  tip.style.display = 'block';
  tip.innerHTML = `
    <h4>${d.name}</h4>
    ${d.tagline ? `<div class="tip-sub">${d.tagline}</div>` : ''}
    <div class="tip-tags">${(d.ai_focus||[]).map(f => `<span class="tip-tag">${f}</span>`).join('')}</div>
    <div class="tip-meta">${d.company_type || ''} · risk: ${d.overall_risk || 'N/A'}</div>
  `;
  moveTooltip(event);
}
function moveTooltip(event) {
  const tip = document.getElementById('tooltip');
  const x = event.clientX + 14, y = event.clientY - 10;
  tip.style.left = Math.min(x, window.innerWidth - 240) + 'px';
  tip.style.top = Math.max(y, 10) + 'px';
}
function hideTooltip() { document.getElementById('tooltip').style.display = 'none'; }

// ── Selection ─────────────────────────────────────────────────────────────────
function selectNode(id) {
  selectedId = id;
  const connectedIds = new Set([id]);
  const connectedEdgeKeys = new Set();
  for (const e of activeEdges) {
    const src = e.source.id || e.source, tgt = e.target.id || e.target;
    if (src === id || tgt === id) {
      connectedIds.add(src); connectedIds.add(tgt);
      connectedEdgeKeys.add(`${src}-${tgt}-${e.type}`);
    }
  }

  nodeSel.classed('dimmed', d => !connectedIds.has(d.id));
  nodeSel.classed('highlighted', d => d.id === id);
  linkSel.classed('dimmed', d => {
    const src = d.source.id || d.source, tgt = d.target.id || d.target;
    return !connectedEdgeKeys.has(`${src}-${tgt}-${d.type}`);
  });

  const node = allNodes.find(n => n.id === id);
  if (node) openPanel(node, activeEdges);

  document.getElementById('canvas-area').classList.add('panel-open');
  document.getElementById('right-panel').classList.add('open');
}

function deselect() {
  selectedId = null;
  nodeSel.classed('dimmed', false).classed('highlighted', false);
  linkSel.classed('dimmed', false);
  document.getElementById('canvas-area').classList.remove('panel-open');
  document.getElementById('right-panel').classList.remove('open');
  simulation.alpha(0.3).restart();
}

document.getElementById('panel-close').addEventListener('click', deselect);

// ── Detail panel ──────────────────────────────────────────────────────────────
function openPanel(node, edges) {
  document.getElementById('panel-name').textContent = node.name;
  document.getElementById('panel-tagline').textContent = node.tagline || '';

  const connections = [];
  for (const e of edges) {
    const src = e.source.id || e.source, tgt = e.target.id || e.target;
    if (src === node.id || tgt === node.id) {
      const otherId = src === node.id ? tgt : src;
      const other = allNodes.find(n => n.id === otherId);
      if (other) connections.push({ name: other.name, type: e.type, weight: e.weight });
    }
  }

  document.getElementById('panel-body').innerHTML = buildPanelHTML(node, connections);
}

function fmt(v) { return v != null ? String(v) : '—'; }
function fmtUSD(v) { if (!v) return '—'; return v >= 1e9 ? `$${(v/1e9).toFixed(1)}B` : v >= 1e6 ? `$${(v/1e6).toFixed(1)}M` : `$${v.toLocaleString()}`; }
function riskBadge(r) { return `<span class="risk-badge ${r||'not_applicable'}">${(r||'N/A').toUpperCase().replace('_',' ')}</span>`; }
function tags(arr, cls='') { return (arr||[]).map(t => `<span class="tag ${cls}">${t}</span>`).join(''); }

function buildPanelHTML(n, connections) {
  const hq = (n.offices||[]).find(o => o.is_hq) || n.offices[0] || {};
  const otherOffices = (n.offices||[]).filter(o => !o.is_hq).map(o => `${o.city}, ${o.country}`).join(' · ') || '—';

  let html = '';

  // Overview
  if (n.description_long) {
    html += `<div class="panel-section"><h3>Overview</h3><p>${n.description_long}</p></div><hr class="panel-divider">`;
  }

  // Classification
  html += `<div class="panel-section"><h3>Classification</h3>
    <div class="tag-row" style="margin-bottom:6px">${tags(n.ai_focus)}</div>
    <table class="kv-table">
      <tr><td>Industries</td><td>${(n.industries_served||[]).join(' · ') || '—'}</td></tr>
      <tr><td>Type</td><td>${fmt(n.business_type)} · ${fmt(n.company_type)}</td></tr>
      <tr><td>AI Native</td><td>${n.is_ai_native ? '✓ Yes' : 'No'}</td></tr>
    </table>
  </div><hr class="panel-divider">`;

  // Quick Facts
  html += `<div class="panel-section"><h3>Quick Facts</h3>
    <table class="kv-table">
      <tr><td>Founded</td><td>${fmt(n.founded_year)}</td></tr>
      <tr><td>Employees</td><td>${fmt(n.employees_range)}</td></tr>
      <tr><td>HQ</td><td>${hq.city ? `${hq.city}, ${hq.country}` : '—'}</td></tr>
      <tr><td>Other offices</td><td>${otherOffices}</td></tr>
      <tr><td>Model</td><td>${fmt(n.business_model)}</td></tr>
      <tr><td>Public</td><td>${n.publicly_traded ? '✓ Yes' : 'No'}</td></tr>
      ${n.stock_ticker ? `<tr><td>Ticker</td><td>${n.stock_ticker}</td></tr>` : ''}
      ${n.parent_company ? `<tr><td>Parent</td><td>${n.parent_company}</td></tr>` : ''}
    </table>
  </div><hr class="panel-divider">`;

  // Financials
  let fundingRows = '';
  for (const r of (n.funding_rounds||[])) {
    fundingRows += `<tr>
      <td>${r.date||'—'}</td>
      <td>${r.type||'—'}</td>
      <td>${r.amount_usd ? fmtUSD(r.amount_usd) : '—'}</td>
      <td style="color:#888">${r.lead_investor||''}</td>
    </tr>`;
  }
  html += `<div class="panel-section"><h3>Financials</h3>
    <table class="kv-table" style="margin-bottom:6px">
      <tr><td>Total raised</td><td>${fmtUSD(n.funding_total_usd)}</td></tr>
      <tr><td>Investors</td><td>${(n.investors||[]).join(', ') || '—'}</td></tr>
    </table>
    ${fundingRows ? `<table style="width:100%;font-size:11px;border-collapse:collapse;color:#888">
      <tr style="color:#555;font-size:10px"><td>Date</td><td>Type</td><td>Amount</td><td>Lead</td></tr>
      ${fundingRows}
    </table>` : ''}
  </div><hr class="panel-divider">`;

  // History
  const milestones = (n.key_milestones||[]).map(m => `<li>${m.year}: ${m.event}</li>`).join('');
  html += `<div class="panel-section"><h3>History &amp; Founders</h3>
    ${n.founders?.length ? `<p style="margin-bottom:4px">${n.founders.join(', ')}</p>` : ''}
    ${n.origin_story ? `<p style="margin-bottom:6px">${n.origin_story}</p>` : ''}
    ${milestones ? `<ul style="margin-left:14px;font-size:11px;color:#888">${milestones}</ul>` : ''}
  </div><hr class="panel-divider">`;

  // Leadership
  const leaders = (n.leadership||[]).map(l => `<tr><td>${l.name}</td><td style="color:#888">${l.role}</td></tr>`).join('');
  const notable = (n.notable_people||[]).map(l => `<tr><td>${l.name}</td><td style="color:#888">${l.role}</td></tr>`).join('');
  if (leaders || notable) {
    html += `<div class="panel-section"><h3>Leadership</h3>
      <table class="kv-table">${leaders}${notable}</table>
    </div><hr class="panel-divider">`;
  }

  // Careers
  const rolesList = (n.open_roles||[]).slice(0, 8).map(r => `<li>${r.title}</li>`).join('');
  html += `<div class="panel-section"><h3>Careers</h3>
    <table class="kv-table" style="margin-bottom:6px">
      <tr><td>Hiring</td><td>${fmt(n.hiring_signals)}</td></tr>
      <tr><td>Open roles</td><td>${fmt(n.open_roles_count)}</td></tr>
      ${n.careers_url ? `<tr><td>URL</td><td><a href="${n.careers_url}" target="_blank" style="color:#4fa3e0">${n.careers_url}</a></td></tr>` : ''}
    </table>
    <div class="tag-row" style="margin-bottom:${rolesList ? '6px' : '0'}">${tags(n.tech_stack, 'green')}</div>
    ${rolesList ? `<ul style="margin-left:14px;font-size:11px;color:#888">${rolesList}</ul>` : ''}
  </div><hr class="panel-divider">`;

  // Glassdoor
  if (n.glassdoor_rating != null || n.glassdoor_reviews != null) {
    html += `<div class="panel-section"><h3>Glassdoor</h3>
      <table class="kv-table">
        ${n.glassdoor_rating != null ? `<tr><td>Rating</td><td>${n.glassdoor_rating} ★</td></tr>` : ''}
        ${n.glassdoor_reviews != null ? `<tr><td>Reviews</td><td>${n.glassdoor_reviews}</td></tr>` : ''}
        ${n.glassdoor_recommend != null ? `<tr><td>Recommend</td><td>${n.glassdoor_recommend}%</td></tr>` : ''}
        ${n.glassdoor_url ? `<tr><td>URL</td><td><a href="${n.glassdoor_url}" target="_blank" style="color:#4fa3e0">glassdoor.com</a></td></tr>` : ''}
      </table>
    </div><hr class="panel-divider">`;
  }

  // Recognition
  const awards = (n.awards||[]).map(a => `<li>${a}</li>`).join('');
  html += `<div class="panel-section"><h3>Recognition</h3>
    ${awards ? `<ul style="margin-left:14px;font-size:11px;color:#888;margin-bottom:6px">${awards}</ul>` : ''}
    <table class="kv-table">
      ${n.customer_count ? `<tr><td>Customers</td><td>${n.customer_count.toLocaleString()}</td></tr>` : ''}
      ${n.notable_clients?.length ? `<tr><td>Clients</td><td>${n.notable_clients.join(', ')}</td></tr>` : ''}
      ${n.partnerships?.length ? `<tr><td>Partners</td><td>${n.partnerships.join(', ')}</td></tr>` : ''}
    </table>
  </div><hr class="panel-divider">`;

  // Risk Assessment
  html += `<div class="panel-section"><h3>Risk Assessment</h3>
    <div class="risk-row">${riskBadge(n.agi_displacement)}<span class="risk-rationale"><strong>AGI:</strong> ${n.agi_displacement_rationale||'—'}</span></div>
    <div class="risk-row">${riskBadge(n.market_risk)}<span class="risk-rationale"><strong>Market:</strong> ${n.market_risk_rationale||'—'}</span></div>
    <div class="risk-row">${riskBadge(n.funding_risk)}<span class="risk-rationale"><strong>Funding:</strong> ${n.funding_risk_rationale||'—'}</span></div>
    <hr class="panel-divider" style="margin:4px 0">
    <div class="risk-row">${riskBadge(n.overall_risk)}<span class="risk-rationale"><strong>Overall:</strong> ${n.overall_risk_rationale||'—'}</span></div>
  </div><hr class="panel-divider">`;

  // Graph Connections
  if (connections.length) {
    const byType = {};
    for (const c of connections) {
      if (!byType[c.type]) byType[c.type] = [];
      byType[c.type].push(c.name);
    }
    let connHTML = '';
    for (const [type, names] of Object.entries(byType)) {
      connHTML += names.map(name =>
        `<div style="font-size:12px;color:#ccc;margin-bottom:2px">
          <span class="conn-dot" style="background:${EDGE_COLORS[type]}"></span>${name}
          <span style="color:#555;font-size:10px">${type}</span>
        </div>`
      ).join('');
    }
    html += `<div class="panel-section"><h3>Graph Connections (${connections.length})</h3>${connHTML}</div><hr class="panel-divider">`;
  }

  // Footer
  html += `<div class="panel-footer">
    ${n.website ? `<a href="${n.website}" target="_blank">↗ ${n.website.replace(/^https?:\/\//, '')}</a>` : '<span></span>'}
    <span>${n.data_quality || ''} · ${(n.scraped_at||'').slice(0,10)}</span>
  </div>`;

  return html;
}

// ── Filters ───────────────────────────────────────────────────────────────────
function applyFilters() {
  const nodeFilter = document.getElementById('filter-nodes').value;
  const minWeight = +document.getElementById('min-weight').value;
  const activeTypes = ['ai_focus', 'investor', 'industry', 'partnership']
    .filter(t => document.getElementById(`toggle-${t}`).checked);

  activeNodes = allNodes.filter(n => {
    if (nodeFilter === 'company') return n.category === 'company';
    if (nodeFilter === 'research_group') return n.category === 'research_group';
    if (nodeFilter === 'ai_native') return n.is_ai_native === true;
    return true;
  });

  const activeNodeIds = new Set(activeNodes.map(n => n.id));

  activeEdges = allEdges.filter(e => {
    if (!activeTypes.includes(e.type)) return false;
    if (!activeNodeIds.has(e.source.id || e.source)) return false;
    if (!activeNodeIds.has(e.target.id || e.target)) return false;
    if (e.type !== 'investor' && e.type !== 'partnership' && e.weight < minWeight) return false;
    return true;
  });

  // Re-color nodes if needed
  if (nodeSel) nodeSel.select('circle').attr('fill', d => nodeColor(d));

  render();
}

// ── Search ────────────────────────────────────────────────────────────────────
document.getElementById('search').addEventListener('input', function() {
  const q = this.value.trim().toLowerCase();
  if (!q) {
    nodeSel.classed('dimmed', false).classed('highlighted', false);
    linkSel.classed('dimmed', false);
    return;
  }
  nodeSel.classed('dimmed', d => !d.name.toLowerCase().includes(q));
  nodeSel.classed('highlighted', d => d.name.toLowerCase().includes(q));
  linkSel.classed('dimmed', true);
});

// ── Wire controls ─────────────────────────────────────────────────────────────
function wireControls() {
  ['ai_focus','investor','industry','partnership'].forEach(t => {
    document.getElementById(`toggle-${t}`).addEventListener('change', applyFilters);
  });

  document.getElementById('min-weight').addEventListener('input', function() {
    document.getElementById('min-weight-val').textContent = this.value;
    applyFilters();
  });

  document.getElementById('color-by').addEventListener('change', () => {
    if (nodeSel) nodeSel.select('circle').attr('fill', d => nodeColor(d));
  });

  document.getElementById('filter-nodes').addEventListener('change', applyFilters);

  document.getElementById('gravity').addEventListener('input', function() {
    document.getElementById('gravity-val').textContent = this.value;
    simulation && simulation.alpha(0.3).restart();
  });

  // Unpin on dblclick
  document.getElementById('graph-svg').addEventListener('dblclick', (event) => {
    // handled per-node via D3 below
  });
}
</script>
</body>
</html>
```

- [ ] **Step 2: Serve locally and verify it loads**

```bash
python -m http.server -d docs 8080
```

Open `http://localhost:8080/graph.html` in browser.

Expected: graph renders with force-directed nodes, filter panel on left. Nodes are colored circles. Hovering a node shows a tooltip. Clicking a node opens the detail panel on the right with full company info. Search filters by name.

- [ ] **Step 3: Double-click unpin — add per-node dblclick handler**

The `svgEl` reference in `wireControls` needs to be scoped after graph init. Ensure this is set in `render()` after nodeSel is assigned:

```js
// At the end of render(), after nodeSel assignment:
nodeSel.on('dblclick', (event, d) => { event.stopPropagation(); d.fx = null; d.fy = null; });
```

Add this line at the end of the `render()` function, after the `nodeSel` `.join()` chain and before `simulation.nodes(...)`.

- [ ] **Step 4: Run build-graph and verify graph-data.json is current, then commit**

```bash
uv run build-graph
git add docs/graph.html docs/graph-data.json
git commit -m "feat: add interactive D3 company graph"
```

---

## Task 6: GitHub Pages Setup

**Files:**
- Modify: (GitHub repo settings — manual step)

- [ ] **Step 1: Verify `docs/` has an `index.html` entry point or note the direct URL**

The graph is at `docs/graph.html`. On GitHub Pages (configured for `docs/` branch), it will be at:
`https://<username>.github.io/<repo>/graph.html`

No `index.html` redirect needed unless you want `/` to go there. Optionally create one:

```bash
echo '<meta http-equiv="refresh" content="0; url=graph.html">' > docs/index.html
git add docs/index.html
git commit -m "chore: add docs/index.html redirect to graph"
```

- [ ] **Step 2: Push to GitHub**

```bash
git push origin main
```

- [ ] **Step 3: Enable GitHub Pages in repo settings**

Go to: `Settings → Pages → Source → Deploy from branch → Branch: main, Folder: /docs` → Save.

- [ ] **Step 4: Verify the live URL works**

Wait ~60 seconds, then open `https://danherma.github.io/ai-in-prague/graph.html` (adjust username/repo as needed).

Expected: graph loads, data fetches correctly, all interactions work.

---

## Rebuild Workflow

After scraping more companies, regenerate and commit the data:

```bash
uv run build-graph
git add docs/graph-data.json
git commit -m "data: regenerate graph-data.json"
git push origin main
```
