# AI in Prague — Company Catalog

Prague AI/ML company catalog. Structured JSON profiles for 375 entities (companies, research groups, initiatives).

## Project Structure

- `data/companies_index.json` — master index (id, name, category, source, status)
- `data/companies/{id}.json` — scraped company profiles (~5 KB avg)
- `skills/scrape-company/SKILL.md` — scraping skill (sources, schema, enums, risk guidelines)
- `scripts/dispatch.py` — async orchestrator for parallel agent dispatch
- `scripts/validate_company.py` — JSON validator with auto-fix for enum mismatches
- `scripts/render_leaflets.py` — LaTeX PDF leaflet renderer per company
- `scripts/backfill_risk.py` — heuristic risk assessment backfiller
- `scripts/scrape_startupjobs.py` — StartupJobs.com company discovery
- `templates/company_leaflet.tex` — XeLaTeX A4 leaflet template (Helvetica Neue, blue banner)
- `output/leaflets/{id}.pdf` — rendered PDF leaflets (gitignored)

## Commands

```bash
# Scraping (dispatches parallel Claude Sonnet agents)
uv run scrape --limit 10              # scrape 10 pending companies (5 parallel)
uv run scrape -n 6 --limit 30         # 30 companies, 6 parallel
uv run scrape --ids apify rossum      # specific companies
uv run scrape --rescrape --ids mews   # redo a broken one
uv run scrape --commit                # git commit after each company
uv run scrape --render                # render PDF after each company
uv run scrape --commit --render -n 6 --limit 30  # full pipeline
uv run scrape --dry-run               # preview without running

# Validation
uv run validate "data/companies/*.json"

# PDF rendering (requires MacTeX / xelatex)
uv run render --ids apify             # render specific companies
uv run render --all                   # render all scraped companies
uv run render --limit 10              # render first 10

# StartupJobs discovery
python3 scripts/scrape_startupjobs.py              # dry run — show new companies
python3 scripts/scrape_startupjobs.py --add         # add new ones to index
python3 scripts/scrape_startupjobs.py --max-pages 20 # deeper pagination
```

## Progress

- **Index:** 375 entities (sources: CNAIP 289, other 82, manual 2, startupjobs 2)
- **Scraped:** 136 done, ~200 pending, ~35 dry_run
- **Risk distribution:** 33% low, 38% medium, 17% high, 12% N/A
- **PDF leaflets:** all scraped companies have rendered PDFs

## Scraping Workflow

1. Load the scrape-company skill before scraping
2. Follow source priority: CNAIP -> company website -> search snippets -> funding search -> Glassdoor -> revenue
3. Web access: try WebFetch first, fall back to `brow` CLI with `--profile scraper` if blocked
4. Use EXACTLY the enum values from the skill — copy-paste, do not improvise
5. Every top-level JSON section must exist (overview, classification, history, size, offices, financials, team, careers, glassdoor, recognition, risk_assessment, metadata)
6. The risk_assessment section is REQUIRED (agi_displacement, market_risk, funding_risk, overall_risk — each with rating + rationale)
7. Use `null` for unknown fields — never invent data
8. Run `uv run validate data/companies/{id}.json` after writing each file
9. **Commit after every company is finished** — one commit per company with message: `data: add {company name} ({id})`

## Commit Convention

- Commit each scraped company immediately after it passes validation
- Stage only `data/companies/{id}.json` and `data/companies_index.json`
- Do not batch commits across multiple companies

## LaTeX / PDF Notes

- xelatex path: `/usr/local/texlive/2026/bin/universal-darwin/xelatex` (add to PATH or the script finds it via shutil.which fallback)
- Template uses Helvetica Neue (macOS system font)
- Full-width blue banner with large company name headline
- All JSON data is rendered — no truncation
- URLs shown in readable form for print + clickable digitally

## Index Sources

- **CNAIP** (aiczechia.cz): primary source, 289 entries — skews toward Czech-founded companies and research groups
- **StartupJobs** (startupjobs.com): secondary discovery via API (`/api/offers`), tags: ai, machine-learning, data-science, data-engineering
- **Manual**: companies found through other channels (e.g. Waypoint AI, SimilarWeb) — foreign-registered companies with Prague engineering offices often missing from CNAIP
