import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
INDEX = DATA / "companies_index.json"
COMPANIES = DATA / "companies"
SKILL = ROOT / "skills" / "scrape-company" / "SKILL.md"
VALIDATOR = ROOT / "scripts" / "validate_company.py"

DEFAULT_CONCURRENCY = 5
DEFAULT_MODEL = "sonnet"

ALLOWED_TOOLS = ",".join(
    [
        "Read",
        "Write",
        "Edit",
        "Bash",
        "Glob",
        "Grep",
        "WebFetch",
        "WebSearch",
        "Agent",
        "mcp__playwright__browser_navigate",
        "mcp__playwright__browser_snapshot",
        "mcp__playwright__browser_click",
        "mcp__playwright__browser_close",
        "mcp__playwright__browser_take_screenshot",
        "mcp__playwright__browser_fill_form",
        "mcp__playwright__browser_press_key",
    ]
)


def load_index():
    with open(INDEX) as f:
        return json.load(f)


def save_index(entries):
    with open(INDEX, "w") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def build_prompt(company):
    skill_text = SKILL.read_text()
    record = json.dumps(company, indent=2)
    return f"""You are a research agent. Your task is to scrape data for one Prague AI company and save it as structured JSON.

## Skill Instructions

{skill_text}

## Company Record

```json
{record}
```

## Web Access Strategy

For fetching web pages, follow this priority:

1. **WebFetch first** — fastest and cheapest. Use for all URLs initially.
2. **If WebFetch fails** (403, captcha, empty response, anti-bot block):
   - Use `brow` CLI with a persistent profile for browser-based access.
   - Start session: `brow session new --profile scraper`
   - Navigate: `brow -s 1 navigate "URL"`
   - Read page: `brow -s 1 snapshot`
   - Close when done: `brow session delete 1`
3. **If brow also fails** (login wall, hard captcha): STOP trying that source. Move to the next source in the skill's priority list.

Do NOT spend more than 2 attempts per URL. Move on quickly.

## Task

1. Follow the scraping strategy in the skill (Sources 1-6 in order)
2. Save the JSON output to `data/companies/{company["id"]}.json`
3. Use EXACTLY the enum values listed in the skill. Copy-paste them, do not improvise.
4. CRITICAL: Every top-level section in the JSON schema must exist (overview, classification, history, size, offices, financials, team, careers, glassdoor, recognition, metadata)
5. Use null for unknown fields. Never invent data.
6. Set scraped_at to the current ISO timestamp.

Begin scraping now."""


def validate(company_id):
    path = COMPANIES / f"{company_id}.json"
    if not path.exists():
        return False, "output file missing"
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(path)],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0, result.stdout.strip()


GIT_LOCK = asyncio.Lock()


def update_index_status(company_id, status):
    index = load_index()
    for entry in index:
        if entry["id"] == company_id:
            entry["status"] = status
            break
    save_index(index)


async def git_commit(company_id, company_name):
    async with GIT_LOCK:
        update_index_status(company_id, "done")
        proc = await asyncio.create_subprocess_exec(
            "git",
            "add",
            str(COMPANIES / f"{company_id}.json"),
            str(INDEX),
            cwd=str(ROOT),
        )
        await proc.communicate()
        msg = f"data: add {company_name} ({company_id})\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
        proc = await asyncio.create_subprocess_exec(
            "git",
            "commit",
            "-m",
            msg,
            cwd=str(ROOT),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            print(f"[GIT]   {company_name} — committed")
        else:
            print(f"[GIT]   {company_name} — commit failed: {stderr.decode()[:200]}")


async def scrape_one(sem, company, model, dry_run, commit):
    async with sem:
        cid = company["id"]
        name = company["name"]
        start = time.monotonic()
        print(f"[START] {name} ({cid})")

        if dry_run:
            print(f"[DRY]   {name} — would dispatch agent")
            return cid, "dry_run", 0

        prompt = build_prompt(company)
        proc = await asyncio.create_subprocess_exec(
            "claude",
            "-p",
            prompt,
            "--model",
            model,
            "--allowedTools",
            ALLOWED_TOOLS,
            "--bare",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(ROOT),
        )
        stdout, stderr = await proc.communicate()
        elapsed = time.monotonic() - start

        if proc.returncode != 0:
            print(f"[FAIL]  {name} ({elapsed:.0f}s) — claude exit {proc.returncode}")
            if stderr:
                print(f"        {stderr.decode()[:200]}")
            return cid, "error", elapsed

        ok, detail = validate(cid)
        status = "done" if ok else "needs_review"
        icon = "OK" if ok else "WARN"
        print(f"[{icon:4s}]  {name} ({elapsed:.0f}s) — {detail}")

        if commit and ok:
            await git_commit(cid, name)

        return cid, status, elapsed


async def run(companies, concurrency, model, dry_run, commit):
    sem = asyncio.Semaphore(concurrency)
    tasks = [scrape_one(sem, c, model, dry_run, commit) for c in companies]
    results = await asyncio.gather(*tasks)

    index = load_index()
    id_to_status = {cid: status for cid, status, _ in results}
    for entry in index:
        if entry["id"] in id_to_status and entry["status"] != "done":
            entry["status"] = id_to_status[entry["id"]]
    save_index(index)

    done = sum(1 for _, s, _ in results if s == "done")
    review = sum(1 for _, s, _ in results if s == "needs_review")
    err = sum(1 for _, s, _ in results if s == "error")
    total_time = sum(t for _, _, t in results)
    print(
        f"\nDone: {done}  Review: {review}  Error: {err}  Total time: {total_time:.0f}s"
    )


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Dispatch parallel Claude agents to scrape companies"
    )
    parser.add_argument(
        "-n",
        "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help=f"max parallel agents (default: {DEFAULT_CONCURRENCY})",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"claude model alias (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="max companies to process"
    )
    parser.add_argument(
        "--ids", nargs="+", default=None, help="specific company IDs to scrape"
    )
    parser.add_argument(
        "--category",
        default=None,
        help="filter by category (company, research_group, initiative)",
    )
    parser.add_argument(
        "--rescrape",
        action="store_true",
        help="re-scrape companies even if already done",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show what would be dispatched without running",
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="git commit after each successful scrape",
    )
    args = parser.parse_args()

    index = load_index()

    if args.ids:
        companies = [c for c in index if c["id"] in args.ids]
    else:
        companies = index

    if args.category:
        companies = [c for c in companies if c["category"] == args.category]

    if not args.rescrape:
        companies = [c for c in companies if c["status"] == "pending"]

    if args.limit:
        companies = companies[: args.limit]

    if not companies:
        print("No companies to scrape.")
        return

    print(
        f"Scraping {len(companies)} companies, concurrency={args.concurrency}, model={args.model}"
    )
    print("-" * 60)
    asyncio.run(run(companies, args.concurrency, args.model, args.dry_run, args.commit))


if __name__ == "__main__":
    main()
