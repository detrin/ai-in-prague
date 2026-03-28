# AI in Prague

Structured catalog of 375 AI/ML companies, research groups, and initiatives based in Prague.

Each entity gets a detailed JSON profile covering what they do, team size, funding, tech stack, open roles, Glassdoor ratings, risk assessment, and more.

## Status

- **375/375 entities scraped** (companies, research groups, initiatives)
- **375 PDF leaflets** rendered (one per company)
- **Risk distribution:** ~33% low, ~38% medium, ~17% high, ~12% N/A
- **Sources:** CNAIP (289), other (82), manual (2), StartupJobs (2)

## Quick Start

```bash
uv sync
uv run scrape --limit 10          # scrape 10 companies (10 parallel agents)
uv run validate "data/companies/*.json"
uv run render --all               # render PDF leaflets
```

## Analysis

An EDA notebook is included at `notebooks/eda.ipynb`. Run it with:

```bash
uv run papermill notebooks/eda.ipynb notebooks/eda_out.ipynb
```

Covers:
- Ecosystem overview (entity types, AI-native split, company types)
- Founding year trend and growth curve
- AI focus area heatmap (vs. actively hiring)
- Top 20 industries served
- Size distribution and hiring rate by band
- Funding landscape (top funded, stage breakdown)
- Risk assessment deep-dive (AGI displacement, market, funding)
- Tech stack demand (top 30 technologies)
- Open roles analysis (departments, AI/ML-specific roles)
- Research-to-commercial gap by AI focus area
- **Full company ranking** — composite score: risk (40%) + coolness (35%) + hiring (25%)

## How It Works

The catalog is built by dispatching parallel [Claude Code](https://claude.ai/claude-code) agents, each researching one company. An async orchestrator (`scripts/dispatch.py`) manages the agent pool.

**Data sources** (in priority order):
1. [Czech National AI Platform](https://www.cnaip.cz) entity pages
2. Company websites (homepage, about, careers)
3. Web search snippets (tech.eu, TheRecursive, AIN.Capital)
4. Funding articles
5. Glassdoor ratings (via search snippets)
6. Revenue estimates (best effort)

**Pipeline:** scrape → validate & auto-fix → commit → render PDF

## Project Structure

```
data/
  companies_index.json       # master index (375 entities)
  companies/{id}.json        # scraped company profiles (~5 KB avg)
notebooks/
  eda.ipynb                  # EDA + company ranking notebook
  eda_out.ipynb              # executed output (with charts)
scripts/
  dispatch.py                # async agent orchestrator
  validate_company.py        # JSON validator with auto-fix
  render_leaflets.py         # XeLaTeX PDF leaflet renderer
  backfill_risk.py           # heuristic risk assessment backfiller
  scrape_startupjobs.py      # StartupJobs.com company discovery
output/
  leaflets/{id}.pdf          # rendered PDF leaflets (gitignored)
skills/
  scrape-company/SKILL.md    # agent instructions, schema, enums
templates/
  company_leaflet.tex        # XeLaTeX A4 leaflet template
```

## Usage

```bash
# Scraping
uv run scrape --limit 10              # scrape 10 pending companies (10 parallel)
uv run scrape -n 6 --limit 30         # 30 companies, 6 parallel
uv run scrape --ids apify rossum      # specific companies
uv run scrape --rescrape --ids mews   # redo a broken one
uv run scrape --commit                # git commit after each company
uv run scrape --dry-run               # preview without running

# Validation
uv run validate "data/companies/*.json"

# PDF rendering (requires MacTeX / xelatex)
uv run render --ids apify             # render specific companies
uv run render --all                   # render all companies
uv run render --limit 10              # render first 10

# StartupJobs discovery
python3 scripts/scrape_startupjobs.py        # dry run — show new companies
python3 scripts/scrape_startupjobs.py --add  # add new ones to index
```

## Company JSON Schema

Each profile includes:

| Section | Fields |
|---------|--------|
| **overview** | description, tagline, website |
| **classification** | business type, AI focus areas, industries served, is_ai_native |
| **history** | founded year, founders, milestones |
| **size** | employee range, office count |
| **offices** | city, country, HQ flag |
| **financials** | funding rounds, investors, revenue estimate, business model |
| **team** | leadership, notable people |
| **careers** | open roles, tech stack, hiring signals |
| **glassdoor** | rating, review count |
| **recognition** | awards, notable clients, partnerships |
| **risk_assessment** | AGI displacement, market risk, funding risk, overall risk (each with rating + rationale) |
| **metadata** | data quality, sources used, fields missing |

## Requirements

- [uv](https://docs.astral.sh/uv/) for project management
- [Claude Code](https://claude.ai/claude-code) CLI for agent dispatch
- Python 3.11+
- MacTeX / xelatex (for PDF rendering only)
