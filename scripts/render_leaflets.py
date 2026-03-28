import json
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "company_leaflet.tex"
COMPANIES = ROOT / "data" / "companies"
OUTPUT = ROOT / "output" / "leaflets"


def tex_escape(s):
    if not isinstance(s, str):
        return str(s) if s is not None else "---"
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    return s


def truncate(s, max_len=400):
    if not s or len(s) <= max_len:
        return s
    return s[:max_len].rsplit(" ", 1)[0] + "..."


def risk_badge_char(level):
    mapping = {"high": "h", "medium": "m", "low": "l", "not_applicable": "n"}
    return mapping.get(level, "n")


def fmt_list(items, fallback="---"):
    if not items:
        return fallback
    return ", ".join(tex_escape(str(i)) for i in items)


def fmt_money(amount):
    if not amount:
        return "---"
    if amount >= 1_000_000_000:
        return f"\\${amount / 1_000_000_000:.1f}B"
    if amount >= 1_000_000:
        return f"\\${amount / 1_000_000:.1f}M"
    if amount >= 1_000:
        return f"\\${amount / 1_000:.0f}K"
    return f"\\${amount}"


def tex_escape_url(url):
    return url.replace("%", "\\%").replace("#", "\\#")


def fmt_url(url, label=None):
    if not url:
        return ""
    label = label or url.replace("https://", "").replace("http://", "").rstrip("/")
    return f"\\href{{{tex_escape_url(url)}}}{{{tex_escape(label)}}}"


def build_links(d):
    lines = []
    website = d.get("overview", {}).get("website")
    careers = d.get("careers", {}).get("careers_url")
    cnaip = d.get("overview", {}).get("cnaip_url")
    glassdoor = d.get("glassdoor", {}).get("glassdoor_url")
    if website:
        lines.append(fmt_url(website, "Website"))
    if careers:
        lines.append(fmt_url(careers, "Careers"))
    if cnaip:
        lines.append(fmt_url(cnaip, "CNAIP"))
    if glassdoor:
        lines.append(fmt_url(glassdoor, "Glassdoor"))
    return " \\\\\n".join(lines) if lines else "---"


def build_leadership(team):
    leaders = team.get("leadership") or []
    if not leaders:
        return "---"
    lines = []
    for leader in leaders[:6]:
        name = tex_escape(leader.get("name", ""))
        role = tex_escape(leader.get("role", ""))
        lines.append(f"{name} --- {role}")
    return " \\\\\n".join(lines)


def build_milestones(history):
    milestones = history.get("key_milestones") or []
    if not milestones:
        return ""
    lines = []
    for m in milestones[:5]:
        if isinstance(m, dict):
            year = m.get("year", "")
            event = tex_escape(m.get("event", ""))
            lines.append(f"\\textcolor{{muted}}{{{year}}} {event}")
        else:
            lines.append(tex_escape(str(m)))
    return " \\\\\n".join(lines)


def build_funding_table(fin):
    lines = []
    total = fin.get("funding_total_usd")
    if total:
        lines.append(f"\\textcolor{{muted}}{{Total}} & {fmt_money(total)} \\\\")
    rounds = fin.get("funding_rounds") or []
    for r in rounds[:4]:
        rtype = tex_escape(r.get("type", ""))
        amount = fmt_money(r.get("amount_usd"))
        date = tex_escape(r.get("date", ""))
        lines.append(f"\\textcolor{{muted}}{{{rtype}}} & {amount} ({date}) \\\\")
    investors = fin.get("investors") or []
    if investors:
        lines.append(
            f"\\textcolor{{muted}}{{Investors}} & {fmt_list(investors[:5])} \\\\"
        )
    revenue = fin.get("revenue_estimate_usd")
    if revenue:
        lines.append(f"\\textcolor{{muted}}{{Revenue}} & {fmt_money(revenue)} \\\\")
    return "\n".join(lines) if lines else "\\textcolor{muted}{No data} & --- \\\\"


def build_open_roles(careers):
    roles = careers.get("open_roles") or []
    if not roles:
        return ""
    lines = [
        r"\begin{itemize}[leftmargin=1em,nosep,label={\textcolor{accent}{\textbullet}}]"
    ]
    for r in roles[:8]:
        if isinstance(r, dict):
            title = tex_escape(r.get("title", ""))
            loc = tex_escape(r.get("location", ""))
            loc_str = f" \\textcolor{{muted}}{{{loc}}}" if loc else ""
            lines.append(f"  \\item {{\\scriptsize {title}{loc_str}}}")
        else:
            lines.append(f"  \\item {{\\scriptsize {tex_escape(str(r))}}}")
    if len(roles) > 8:
        lines.append(
            f"  \\item {{\\scriptsize\\textcolor{{muted}}{{+{len(roles) - 8} more}}}}"
        )
    lines.append(r"\end{itemize}")
    return "\n".join(lines)


def build_glassdoor(gl):
    if not gl or not gl.get("rating"):
        lines = ["\\textcolor{muted}{No data} & --- \\\\"]
        return "\n".join(lines)
    lines = []
    lines.append(f"\\textcolor{{muted}}{{Rating}} & {gl['rating']}/5.0 \\\\")
    if gl.get("review_count"):
        lines.append(f"\\textcolor{{muted}}{{Reviews}} & {gl['review_count']} \\\\")
    if gl.get("recommend_pct"):
        lines.append(
            f"\\textcolor{{muted}}{{Recommend}} & {gl['recommend_pct']}\\% \\\\"
        )
    if gl.get("glassdoor_url"):
        lines.append(
            f"\\textcolor{{muted}}{{Link}} & {fmt_url(gl['glassdoor_url'], 'Glassdoor')} \\\\"
        )
    return "\n".join(lines)


def build_offices_list(offices):
    if not offices:
        return "---"
    parts = []
    for o in offices:
        if isinstance(o, dict):
            city = o.get("city", "")
            country = o.get("country", "")
            hq = " (HQ)" if o.get("is_hq") else ""
            parts.append(f"{city}, {country}{hq}")
        else:
            parts.append(str(o))
    return tex_escape("; ".join(parts))


def build_notable_people(tm):
    people = tm.get("notable_people") or []
    if not people:
        return ""
    lines = ["\\sectionhead{Notable People}", "{\\footnotesize"]
    for p in people[:4]:
        if isinstance(p, dict):
            name = tex_escape(p.get("name", ""))
            role = tex_escape(p.get("role", ""))
            lines.append(f"{name} --- {role} \\\\")
        else:
            lines.append(f"{tex_escape(str(p))} \\\\")
    lines.append("}")
    return "\n".join(lines)


def build_recognition(rec):
    parts = []
    clients = rec.get("notable_clients") or []
    if clients:
        parts.append(f"\\textcolor{{muted}}{{Clients:}} {fmt_list(clients)}")
    awards = rec.get("awards") or []
    if awards:
        parts.append(f"\\textcolor{{muted}}{{Awards:}} {fmt_list(awards)}")
    count = rec.get("customer_count")
    if count:
        parts.append(f"\\textcolor{{muted}}{{Customers:}} {tex_escape(str(count))}")
    partnerships = rec.get("partnerships") or []
    if partnerships:
        parts.append(f"\\textcolor{{muted}}{{Partners:}} {fmt_list(partnerships)}")
    return " \\\\\n".join(parts) if parts else "---"


def fill_template(template_text, d):
    ov = d.get("overview", {})
    cl = d.get("classification", {})
    hi = d.get("history", {})
    sz = d.get("size", {})
    fin = d.get("financials", {})
    tm = d.get("team", {})
    ca = d.get("careers", {})
    gl = d.get("glassdoor", {})
    rec = d.get("recognition", {})
    ra = d.get("risk_assessment", {})
    meta = d.get("metadata", {})

    offices = d.get("offices") or []
    hq = next((o for o in offices if o.get("is_hq")), {})
    hq_str = f"{hq.get('city', '---')}, {hq.get('country', '')}" if hq else "---"

    replacements = {
        "VAR_NAME": tex_escape(d.get("name", "")),
        "VAR_CATEGORY": tex_escape(d.get("category", "").replace("_", " ").title()),
        "VAR_TAGLINE": tex_escape(ov.get("tagline") or ov.get("description") or ""),
        "VAR_DESCRIPTION_LONG": tex_escape(
            ov.get("description_long")
            or ov.get("description")
            or "No description available."
        ),
        "VAR_BUSINESS_TYPE": tex_escape(
            (cl.get("business_type") or "---").replace("_", " ").title()
        ),
        "VAR_COMPANY_TYPE": tex_escape(
            (cl.get("company_type") or "---").replace("_", " ").title()
        ),
        "VAR_AI_FOCUS": fmt_list(
            [f.replace("_", " ") for f in (cl.get("ai_focus") or [])]
        ),
        "VAR_INDUSTRIES": fmt_list(cl.get("industries_served")),
        "VAR_AI_NATIVE": "Yes" if cl.get("is_ai_native") else "No",
        "VAR_FOUNDED": tex_escape(str(hi.get("founded_year") or "---")),
        "VAR_EMPLOYEES": tex_escape(
            (sz.get("employees_range") or "---")
            + (f" (~{sz['employees_exact']})" if sz.get("employees_exact") else "")
        ),
        "VAR_OFFICES_LIST": build_offices_list(offices),
        "VAR_HQ": tex_escape(hq_str),
        "VAR_BUSINESS_MODEL": tex_escape(
            (fin.get("business_model") or "---").replace("_", " ").title()
        ),
        "VAR_PUBLICLY_TRADED": "Yes" if fin.get("publicly_traded") else "No",
        "VAR_STOCK_TICKER": tex_escape(
            f"{fin.get('stock_ticker', '')} ({fin.get('stock_exchange', '')})"
            if fin.get("stock_ticker")
            else "---"
        ),
        "VAR_PARENT_COMPANY": tex_escape(fin.get("parent_company") or "---"),
        "VAR_LINKS": build_links(d),
        "VAR_FOUNDERS": fmt_list(hi.get("founders")),
        "VAR_ORIGIN_STORY": tex_escape(hi.get("origin_story") or ""),
        "VAR_MILESTONES": build_milestones(hi),
        "VAR_FUNDING_TABLE": build_funding_table(fin),
        "VAR_GLASSDOOR_TABLE": build_glassdoor(gl),
        "VAR_LEADERSHIP": build_leadership(tm),
        "VAR_NOTABLE_PEOPLE": build_notable_people(tm),
        "VAR_HIRING_SIGNALS": tex_escape(
            (ca.get("hiring_signals") or "---").replace("_", " ").title()
        ),
        "VAR_OPEN_ROLES_COUNT": tex_escape(
            str(ca.get("open_roles_count") or len(ca.get("open_roles") or []) or "---")
        ),
        "VAR_TECH_STACK": fmt_list(ca.get("tech_stack")),
        "VAR_CAREERS_URL": fmt_url(ca.get("careers_url"), "Link")
        if ca.get("careers_url")
        else "---",
        "VAR_OPEN_ROLES": build_open_roles(ca),
        "VAR_RECOGNITION": build_recognition(rec),
        "VAR_RISK_AGI_BADGE": risk_badge_char(ra.get("agi_displacement")),
        "VAR_RISK_AGI_RATIONALE": tex_escape(
            ra.get("agi_displacement_rationale") or "---"
        ),
        "VAR_RISK_MARKET_BADGE": risk_badge_char(ra.get("market_risk")),
        "VAR_RISK_MARKET_RATIONALE": tex_escape(
            ra.get("market_risk_rationale") or "---"
        ),
        "VAR_RISK_FUNDING_BADGE": risk_badge_char(ra.get("funding_risk")),
        "VAR_RISK_FUNDING_RATIONALE": tex_escape(
            ra.get("funding_risk_rationale") or "---"
        ),
        "VAR_RISK_OVERALL_BADGE": risk_badge_char(ra.get("overall_risk")),
        "VAR_RISK_OVERALL_RATIONALE": tex_escape(
            ra.get("overall_risk_rationale") or "---"
        ),
        "VAR_DATA_QUALITY": tex_escape(meta.get("data_quality") or "---"),
        "VAR_SCRAPED_AT": tex_escape((d.get("scraped_at") or "---")[:10]),
        "VAR_SOURCES": fmt_list(meta.get("sources_used")),
        "VAR_ID": tex_escape(d.get("id", "")),
        "VAR_METADATA_NOTES": (
            f"{{\\color{{muted}}\\fontsize{{5.5}}{{6.5}}\\selectfont Notes: {tex_escape(meta['notes'])}}}"
            if meta.get("notes")
            else ""
        ),
    }

    result = template_text
    for key, val in replacements.items():
        result = result.replace(key, val)
    return result


def render_one(json_path, template_text):
    with open(json_path) as f:
        d = json.load(f)

    company_id = d.get("id", json_path.stem)
    tex_content = fill_template(template_text, d)

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = Path(tmpdir) / f"{company_id}.tex"
        tex_path.write_text(tex_content, encoding="utf-8")

        subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "-halt-on-error", str(tex_path)],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=60,
        )

        pdf_path = Path(tmpdir) / f"{company_id}.pdf"
        if pdf_path.exists():
            OUTPUT.mkdir(parents=True, exist_ok=True)
            dest = OUTPUT / f"{company_id}.pdf"
            shutil.copy2(pdf_path, dest)
            return True, str(dest)
        else:
            log_path = Path(tmpdir) / f"{company_id}.log"
            log_tail = ""
            if log_path.exists():
                lines = log_path.read_text(errors="replace").splitlines()
                error_lines = [line for line in lines if line.startswith("!")]
                log_tail = (
                    "\n".join(error_lines[:5])
                    if error_lines
                    else "\n".join(lines[-10:])
                )
            return False, log_tail


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Render company JSON to PDF leaflets")
    parser.add_argument(
        "--ids", nargs="+", default=None, help="specific company IDs to render"
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="max companies to render"
    )
    parser.add_argument("--all", action="store_true", help="render all companies")
    args = parser.parse_args()

    template_text = TEMPLATE.read_text(encoding="utf-8")

    if args.ids:
        paths = [COMPANIES / f"{cid}.json" for cid in args.ids]
        paths = [p for p in paths if p.exists()]
    elif args.all or args.limit:
        paths = sorted(COMPANIES.glob("*.json"))
    else:
        print("Usage: render --ids apify rossum | --all | --limit 10")
        sys.exit(1)

    if args.limit:
        paths = paths[: args.limit]

    if not paths:
        print("No company files found.")
        sys.exit(1)

    print(f"Rendering {len(paths)} leaflet(s)...")
    ok_count = 0
    for p in paths:
        name = p.stem
        success, detail = render_one(p, template_text)
        if success:
            print(f"  [OK]   {name:25s} -> {detail}")
            ok_count += 1
        else:
            print(f"  [FAIL] {name:25s}")
            if detail:
                for line in detail.split("\n")[:3]:
                    print(f"         {line}")

    print(f"\nRendered: {ok_count}/{len(paths)}")


if __name__ == "__main__":
    main()
