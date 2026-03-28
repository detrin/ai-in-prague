# AI in Prague

Structured catalog of 371 AI/ML companies, research groups, and initiatives based in Prague. Built for job seekers exploring the Prague AI ecosystem.

Each entity gets a detailed JSON profile covering what they do, team size, funding, tech stack, open roles, Glassdoor ratings, and more.

## Quick Start

```bash
uv sync
uv run scrape --limit 10          # scrape 10 companies (5 parallel agents)
uv run validate "data/companies/*.json"
```

## How It Works

The catalog is built by dispatching parallel [Claude Code](https://claude.ai/claude-code) agents, each researching one company. An async orchestrator (`scripts/dispatch.py`) manages the agent pool.

**Data sources** (in priority order):
1. [Czech National AI Platform](https://www.cnaip.cz) entity pages
2. Company websites (homepage, about, careers)
3. Web search snippets (tech.eu, TheRecursive, AIN.Capital)
4. Funding articles
5. Glassdoor ratings (via search snippets)
6. Revenue estimates (best effort)

**Pipeline:** scrape → validate & auto-fix → commit

## Project Structure

```
data/
  companies_index.json       # master index (371 entities)
  companies/{id}.json        # scraped company profiles
scripts/
  dispatch.py                # async agent orchestrator
  validate_company.py        # JSON validator with auto-fix
skills/
  scrape-company/SKILL.md    # agent instructions, schema, enums
```

## Usage

```bash
# Scrape specific companies
uv run scrape --ids apify rossum deepnote

# Scrape by category
uv run scrape --category research_group --limit 20

# Increase parallelism
uv run scrape -n 10 --limit 50

# Use a different model
uv run scrape --model opus --limit 5

# Re-scrape failed companies
uv run scrape --rescrape --ids mews good-ai

# Preview without running
uv run scrape --dry-run --limit 50

# Validate all scraped data
uv run validate "data/companies/*.json"
```

## Company JSON Schema

Each profile includes:

| Section | Fields |
|---------|--------|
| **overview** | description, tagline, website |
| **classification** | business type, AI focus areas, industries served |
| **history** | founded year, founders, milestones |
| **size** | employee range, office count |
| **offices** | city, country, HQ flag |
| **financials** | funding rounds, investors, revenue estimate, business model |
| **team** | leadership, notable people |
| **careers** | open roles, tech stack, hiring signals |
| **glassdoor** | rating, review count |
| **recognition** | awards, notable clients |
| **metadata** | data quality, sources used |

## Requirements

- [uv](https://docs.astral.sh/uv/) for project management
- [Claude Code](https://claude.ai/claude-code) CLI for agent dispatch
- Python 3.11+
