# AI in Prague — Company Catalog

Prague AI/ML company catalog for job seekers. Structured JSON profiles for 371 companies, research groups, and initiatives.

## Project Structure

- `data/companies_index.json` — master index of all entities (id, name, category, status)
- `data/companies/{id}.json` — scraped company profiles
- `skills/scrape-company/SKILL.md` — scraping skill (sources, schema, enums)
- `scripts/dispatch.py` — async orchestrator for parallel agent dispatch
- `scripts/validate_company.py` — post-write validator with auto-fix

## Commands

```bash
uv run scrape --limit 10              # scrape 10 pending companies (5 parallel)
uv run scrape -n 3 --limit 20         # 20 companies, 3 parallel
uv run scrape --ids apify rossum      # specific companies
uv run scrape --rescrape --ids mews   # redo a broken one
uv run scrape --dry-run               # preview without running
uv run validate "data/companies/*.json"
```

## Scraping Workflow

1. Load the scrape-company skill before scraping
2. Follow source priority: CNAIP -> company website -> search snippets -> funding search -> Glassdoor -> revenue
3. Web access: try WebFetch first, fall back to `brow` CLI with `--profile scraper` if blocked
4. Use EXACTLY the enum values from the skill — copy-paste, do not improvise
5. Every top-level JSON section must exist (overview, classification, history, size, offices, financials, team, careers, glassdoor, recognition, metadata)
6. Use `null` for unknown fields — never invent data
7. Run `uv run validate data/companies/{id}.json` after writing each file
8. **Commit after every company is finished** — one commit per company with message: `data: add {company name} ({id})`

## Commit Convention

- Commit each scraped company immediately after it passes validation
- Stage only `data/companies/{id}.json` and `data/companies_index.json`
- Do not batch commits across multiple companies
