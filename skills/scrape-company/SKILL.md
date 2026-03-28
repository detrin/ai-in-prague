---
name: scrape-company
description: Use when researching a Prague AI company to build its catalog entry. Defines what data to collect, where to look, and the exact JSON output schema.
---

# Scrape Company

Collect structured data on a Prague AI/ML company for the job-seeker catalog. One company per invocation. Output is a single JSON file saved to `data/companies/{id}.json`.

## Input

The agent receives a company record from `data/companies_index.json`:

```json
{"id": "rossum", "name": "Rossum", "category": "company", "cnaip_url": "https://www.cnaip.cz/cs/entity/rossum", "website_url": "https://rossum.ai"}
```

## Scraping Strategy (ordered by reliability)

### Source 1 — CNAIP page (ALWAYS start here if available)

CNAIP pages are consistent and scrapable. Navigate to `cnaip_url`, take snapshot. Extract: description, tags, team members, links to company website.

### Source 2 — Company website

Use `website_url` from index (do NOT waste time searching for it). Visit in order:
1. Homepage — tagline, what they do
2. About/Company page — founding year, history, team size, offices
3. Careers page — open roles, tech stack signals

**If the site blocks you** (captcha, anti-bot, redirect): STOP. Do not retry. Move to Source 3.

### Source 3 — Search snippets (fallback)

Search for `"{company_name}" Prague AI` and extract from snippets. Good sources:
- tech.eu, TheRecursive, AIN.Capital articles
- Tracxn, Owler summaries (often in snippets)
- LinkedIn company page snippets

### Source 4 — Funding (best effort only)

Search `"{company_name}" funding raised series site:tech.eu OR site:therecursive.com OR site:ain.capital`. Do NOT attempt Crunchbase or PitchBook (they block automated access).

### Source 5 — Glassdoor

Search `"{company_name}" glassdoor rating reviews`. Extract:
- Overall rating (1.0-5.0)
- Number of reviews
- "Recommend to a friend" percentage (if visible in snippet)

Do NOT navigate to glassdoor.com directly (login wall). Use search snippets only.

### Source 6 — Revenue (best effort only)

Search `"{company_name}" revenue ARR`. Accept whatever snippets return. Do NOT spend more than 2 searches on this — revenue data for private Czech companies is rarely public.

## Enum Values (MANDATORY — use EXACTLY these values)

**Copy-paste from this list. Do not improvise.**

```
business_type:      b2b_saas | b2c_saas | consulting | product | research | enterprise_vendor | other
company_type:       startup | scaleup | enterprise | acquired | research_lab | nonprofit
ai_focus:           nlp | cv | ml_ops | generative_ai | robotics | data_engineering | fraud_detection | recommendation | speech | automation | document_processing | other
employees_range:    1-10 | 11-50 | 51-200 | 201-500 | 501-1000 | 1001-5000 | 5000+
business_model:     subscription_saas | usage_based | consulting_services | licensing | marketplace | freemium | other
hiring_signals:     actively_hiring | few_roles | not_hiring | unknown
data_quality:       high | medium | low
risk_level:         high | medium | low | not_applicable
```

**Rules:**
- `employees_range` — round to nearest bucket (e.g. 70 employees → "51-200", NOT "51-100")
- `business_type` — use "b2b_saas" not "B2B", "B2B SaaS", etc.
- `data_quality` — high = 3+ sources, medium = 1-2 sources, low = estimated/inferred
- If you're unsure which enum value to use, pick the closest match or use "other"

## JSON Output Schema

Save to `data/companies/{id}.json`:

```json
{
  "id": "rossum",
  "name": "Rossum",
  "category": "company",
  "scraped_at": "2026-03-28T12:00:00Z",

  "overview": {
    "description": "AI document processing for transactional workflows",
    "description_long": "Rossum builds AI agents that read documents, capture and validate data, send emails, handle approvals, and write to ERPs. Proprietary transactional LLM supporting 276 languages.",
    "tagline": "Offload paperwork to AI agents",
    "website": "https://rossum.ai",
    "cnaip_url": "https://www.cnaip.cz/cs/entity/rossum"
  },

  "classification": {
    "business_type": "b2b_saas",
    "ai_focus": ["document_processing", "nlp", "cv"],
    "industries_served": ["finance", "logistics", "retail", "manufacturing"],
    "company_type": "scaleup",
    "is_ai_native": true
  },

  "history": {
    "founded_year": 2017,
    "founders": ["Tomáš Gogar", "Petr Baudiš", "Tomáš Tunys"],
    "origin_story": "Founded by 3 Czech PhD students in AI",
    "key_milestones": [
      {"year": 2017, "event": "Founded in Prague"},
      {"year": 2024, "event": "Named in Sifted B2B SaaS Rising 100"}
    ]
  },

  "size": {
    "employees_range": "201-500",
    "employees_exact": null,
    "employee_source": "company_website",
    "office_count": 5
  },

  "offices": [
    {"city": "Prague", "country": "CZ", "is_hq": true},
    {"city": "London", "country": "GB", "is_hq": false}
  ],

  "financials": {
    "publicly_traded": false,
    "stock_ticker": null,
    "stock_exchange": null,
    "parent_company": null,
    "funding_total_usd": null,
    "funding_rounds": [
      {"date": "2021-06", "type": "Series A", "amount_usd": 10000000, "lead_investor": "Some VC"}
    ],
    "investors": ["Investor A", "Investor B"],
    "revenue_estimate_usd": null,
    "revenue_source": null,
    "business_model": "subscription_saas"
  },

  "team": {
    "leadership": [
      {"name": "Tomáš Gogar", "role": "CEO", "source": "company_website"}
    ],
    "notable_people": []
  },

  "careers": {
    "careers_url": "https://rossum.ai/careers/",
    "open_roles_count": null,
    "open_roles": [
      {"title": "ML Engineer", "department": "engineering", "location": "Prague"}
    ],
    "tech_stack": ["python", "typescript", "aws"],
    "hiring_signals": "actively_hiring"
  },

  "glassdoor": {
    "rating": 4.2,
    "review_count": 35,
    "recommend_pct": 85,
    "glassdoor_url": "https://www.glassdoor.com/Overview/Working-at-Rossum-EI_IE..."
  },

  "recognition": {
    "awards": ["IDC Leader 2023", "G2 Leader Fall 2024"],
    "notable_clients": ["Siemens", "Bosch", "Wolt", "Adyen"],
    "customer_count": 450,
    "partnerships": []
  },

  "risk_assessment": {
    "agi_displacement": "low",
    "agi_displacement_rationale": "Proprietary transactional LLM trained on domain-specific document data across 276 languages. Deep vertical moat in document processing with enterprise integrations that foundation models cannot easily replicate.",
    "market_risk": "medium",
    "market_risk_rationale": "IDP market is growing but increasingly competitive with Microsoft, Google, and AWS offering native document AI. Rossum differentiates on workflow automation beyond pure extraction.",
    "funding_risk": "low",
    "funding_risk_rationale": "Well-funded scaleup with 450+ paying enterprise customers and strong revenue signals (Sifted Rising 100).",
    "overall_risk": "low",
    "overall_risk_rationale": "Strong proprietary tech moat, established enterprise customer base, and vertical focus in regulated industries provide resilience against AGI commoditization."
  },

  "metadata": {
    "data_quality": "high",
    "sources_used": ["company_website", "cnaip", "tech.eu"],
    "fields_missing": ["funding_total_usd", "revenue_estimate_usd"],
    "needs_review": false,
    "notes": ""
  }
}
```

## Risk Assessment Guidelines

Every company MUST have a `risk_assessment` section. Assess based on what you learned during scraping. Use `risk_level` enum: `high | medium | low | not_applicable`.

### AGI Displacement Risk
How likely foundation models (GPT, Claude, Gemini) will commoditize this company's core value proposition.
- **high**: Thin wrapper around LLM APIs, generic chatbot/automation, no proprietary data or tech. Easy to replicate with a prompt.
- **medium**: Vertical SaaS with some domain expertise, but core AI capability is becoming commoditized. Has customer lock-in that buys time.
- **low**: Deep proprietary data moat, infrastructure layer that AGI still needs, regulated domain requiring compliance/certification, or hardware/robotics.
- **not_applicable**: Research groups, nonprofits, government initiatives.

### Market Risk
Is the market real, sustainable, and big enough?
- **high**: Hype-driven niche, no clear PMF, tiny addressable market, or dominated by well-funded incumbents.
- **medium**: Real market but competitive, or dependent on a single trend/platform.
- **low**: Established market with proven demand and paying customers.
- **not_applicable**: Research groups.

### Funding Risk
Can the company survive long enough to reach sustainability?
- **high**: No known funding, pre-revenue, small team with no runway signals.
- **medium**: Some funding but early stage, or bootstrapped with revenue but unclear margins.
- **low**: Well-funded (Series A+), profitable, or backed by large parent company.
- **not_applicable**: Research groups (grant-funded), acquired companies, enterprise subsidiaries.

### Overall Risk
Weighted judgment across all factors. A company with high AGI displacement risk but low market and funding risk might be medium overall.

**Rationale is required** for every risk rating — 1-2 sentences explaining why, referencing specific facts from your research (product type, funding, customer base, tech moat).

## Null Handling

Use `null` for unknown fields. **Never invent data.** If estimated, note source in `metadata.sources_used` and set `data_quality` accordingly.

## Research Group Adaptation

For `category: "research_group"`:
- `classification.business_type` = "research"
- `classification.company_type` = "research_lab"
- `financials` — focus on grants, not funding rounds
- `careers` — PhD positions, postdocs, research assistants
- `team.leadership` — PI / group lead
- `recognition` — top publications, h-index of PI

## Agent Dispatch Pattern

To scrape multiple companies, dispatch parallel agents (max 5-10 at a time):

```
for each batch of companies from companies_index.json where status == "pending":
  dispatch agents, each with:
    - company record from index
    - this skill loaded
  on completion:
    - save {id}.json to data/companies/
    - run validate_company.py on the output
    - update companies_index.json status to "done"
```

## Post-Write Validation

After writing JSON, the orchestrator MUST run `python3 scripts/validate_company.py data/companies/{id}.json` to catch enum mismatches and missing required fields. If validation fails, fix the file before marking the company as done.
