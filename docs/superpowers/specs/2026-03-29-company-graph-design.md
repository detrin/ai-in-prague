# Company Relationship Graph — Design Spec

**Date:** 2026-03-29
**Status:** Approved
**Goal:** Interactive 2D force-directed graph for personal exploration of the Prague AI company catalog, deployable as a static file on GitHub Pages.

---

## Architecture

Two-part build:

1. **`scripts/build_graph.py`** — reads all `data/companies/*.json`, extracts nodes and edges, writes `docs/graph-data.json`. Registered as `uv run build-graph`.
2. **`docs/graph.html`** — self-contained D3 v7 app that fetches `graph-data.json` at load time and renders. No server needed. Hosted via GitHub Pages from the `docs/` folder.

The HTML file loads D3 from CDN. All company data is in `graph-data.json` (separate file, not inlined, to keep `graph.html` maintainable).

---

## Data Pipeline — `build_graph.py`

Reads only files with `status: "done"` from the index. For each company JSON, extracts:

**Node fields:**
- `id`, `name`, `category` (company / research_group / initiative)
- `classification.ai_focus[]`, `classification.industries_served[]`, `classification.company_type`, `classification.business_type`, `classification.is_ai_native`
- `size.employees_range`
- `risk_assessment.overall_risk`
- `financials.investors[]`, `financials.funding_total_usd`, `financials.funding_rounds[]`, `financials.business_model`, `financials.publicly_traded`, `financials.parent_company`
- `history.founded_year`, `history.founders[]`, `history.origin_story`, `history.key_milestones[]`
- `overview.description_long`, `overview.tagline`, `overview.website`
- `team.leadership[]`, `team.notable_people[]`
- `careers.hiring_signals`, `careers.open_roles_count`, `careers.open_roles[]`, `careers.tech_stack[]`, `careers.careers_url`
- `glassdoor.*`
- `recognition.awards[]`, `recognition.notable_clients[]`, `recognition.customer_count`, `recognition.partnerships[]`
- `risk_assessment.*` (all four ratings + rationales)
- `offices[]`
- `metadata.data_quality`, `metadata.scraped_at`, `metadata.sources_used[]`, `metadata.notes`

**Edge extraction** (four types):

| Type | Source | Edge condition | Weight |
|------|--------|----------------|--------|
| `ai_focus` | `classification.ai_focus[]` | Two companies share ≥1 tag | Count of shared tags |
| `investor` | `financials.investors[]` | Two companies share ≥1 investor | Count of shared investors |
| `industry` | `classification.industries_served[]` | Two companies share ≥1 industry | Count of shared industries |
| `partnership` | `recognition.partnerships[]` | Partnership name matches another node's `name` (case-insensitive exact match only, against nodes present in the graph) | 1 |

Output schema:
```json
{
  "nodes": [{ "id": "apify", "name": "Apify", ... }],
  "edges": [{ "source": "apify", "target": "rossum", "type": "ai_focus", "weight": 2 }]
}
```

---

## Graph Rendering — `graph.html`

**Library:** D3.js v7 from CDN — `https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js`

### Layout

D3 force simulation with:
- `d3.forceManyBody()` — repulsion between all nodes
- `d3.forceLink()` — attraction along edges, strength proportional to `weight`
- `d3.forceCenter()` — centering
- **Cluster gravity** — weak custom force pulling each node toward the centroid of its dominant `ai_focus` cluster. Strength controlled by a slider (0 = free, 10 = strong clustering).

### Node visual encoding

| Property | Visual |
|----------|--------|
| `employees_range` | Node radius (5px for 1–10 up to 18px for 1000+) |
| `category` / `classification.*` | Node fill color (see Color schemes below) |
| `overall_risk` | Stroke width (low=1px, medium=2px, high=3.5px, red stroke for high) |
| `name` | Label on hover |

**Color schemes** (switchable via "Color by" dropdown):
- **Category**: company=blue, research_group=red, initiative=orange
- **Primary AI focus**: distinct color per top ai_focus tag (automation, nlp, cv, generative_ai, etc.)
- **Company type**: startup, scaleup, enterprise, etc.
- **Overall risk**: green=low, amber=medium, red=high

### Edge visual encoding

| Type | Color | Opacity | Stroke style |
|------|-------|---------|--------------|
| `ai_focus` | `#4fa3e0` blue | 0.3–0.6 scaled by weight | solid |
| `investor` | `#f5a623` orange | 0.5–0.8 | solid |
| `industry` | `#7ed321` green | 0.2–0.4 scaled by weight | dashed |
| `partnership` | `#e05c5c` red | 0.8 | solid, thicker |

---

## UI Layout

Three-panel layout:

```
┌─────────────────────────────────────────────────────────────┐
│  Prague AI Graph     [search...]              136 nodes      │  ← top bar
├──────────┬──────────────────────────────┬───────────────────┤
│  Filters │                              │  Company Detail   │
│          │       D3 canvas              │  (scrollable,     │
│  edge    │   zoom · pan · drag          │   360px wide,     │
│  toggles │                              │   shown on click) │
│  sliders │                              │                   │
│  color   │                              │                   │
└──────────┴──────────────────────────────┴───────────────────┘
```

### Left panel — Filters (220px, fixed)

- **Edge type toggles** — checkbox per type (ai_focus, investor, industry, partnership), color-coded
- **Min shared tags slider** — filters out weak edges (1–5); default 2. Applied to ai_focus and industry edges only.
- **Color by** — dropdown: Category / Primary AI focus / Company type / Overall risk
- **Filter nodes** — dropdown: All / Companies only / Research groups / AI-native only
- **Cluster gravity** — slider 0–10, default 4

### Center — Graph canvas (flex, fills remaining space)

- Zoom (scroll wheel) and pan (drag background)
- Drag individual nodes (pins them; double-click to unpin)
- Hover node → tooltip (name, tagline, ai_focus tags, company_type, risk badge)
- Click node → opens right panel, highlights connected nodes, dims others
- Click background → deselects

### Right panel — Company detail (360px, hidden until node click)

Scrollable panel with sticky blue header (name + tagline + close ×). Sections mirror the PDF leaflet exactly:

1. **Overview** — description_long
2. **Classification** — ai_focus tag pills, industries_served, is_ai_native, business_type
3. **Quick Facts** — founded, employees, HQ, offices, business_model, publicly_traded, ticker, parent
4. **Financials** — funding_total, funding rounds table (date / type / amount / lead investor), investors list
5. **History** — founders, origin_story, key_milestones timeline
6. **Leadership** — name + role list; notable_people if present
7. **Careers** — hiring_signals, open_roles_count, tech_stack tags, careers_url link, open roles list
8. **Glassdoor** — rating, review_count, recommend_pct, link
9. **Recognition** — awards, notable_clients, customer_count, partnerships
10. **Risk Assessment** — four risk rows (AGI displacement, market, funding, overall), each with badge + rationale
11. **Graph Connections** — list of connected nodes grouped by edge type with color dot
12. **Footer** — website link, data_quality, scraped_at, sources

---

## File Output

```
docs/
  graph.html          ← D3 app (static, ~500 lines)
  graph-data.json     ← generated by build_graph.py
scripts/
  build_graph.py      ← data pipeline
```

Add to `.gitignore`: `.superpowers/`
Add to `pyproject.toml` scripts: `build-graph = "scripts.build_graph:main"`

---

## Build Command

```bash
uv run build-graph       # regenerate docs/graph-data.json
python -m http.server -d docs 8080  # local preview (fetch() needs HTTP, not file://)
# open http://localhost:8080/graph.html
# or push docs/ to GitHub Pages — works without a server
```

---

## Out of Scope

- Authentication / access control
- Real-time data updates
- Mobile layout
- Export / share functionality
- Backend server of any kind
