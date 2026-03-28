import json
import glob
import sys

RISK_LEVELS = {"high", "medium", "low", "not_applicable"}


def assess_agi_displacement(d):
    focuses = d.get("classification", {}).get("ai_focus") or []
    btype = d.get("classification", {}).get("business_type", "")
    ctype = d.get("classification", {}).get("company_type", "")
    desc = (
        d.get("overview", {}).get("description_long")
        or d.get("overview", {}).get("description")
        or ""
    ).lower()
    emp = d.get("size", {}).get("employees_range", "")
    clients = d.get("recognition", {}).get("notable_clients") or []

    if ctype in ("research_lab", "nonprofit"):
        return (
            "not_applicable",
            "Research/nonprofit entity — not subject to commercial displacement.",
        )

    infra_focuses = {
        "data_engineering",
        "robotics",
        "cv",
        "fraud_detection",
        "speech",
        "document_processing",
    }
    wrapper_focuses = {"generative_ai", "automation", "nlp"}

    has_infra = bool(set(focuses) & infra_focuses)
    has_wrapper = bool(set(focuses) & wrapper_focuses)
    has_clients = len(clients) >= 3
    is_large = emp in ("201-500", "501-1000", "1001-5000", "5000+")

    proprietary_signals = any(
        kw in desc
        for kw in [
            "proprietary",
            "patent",
            "own model",
            "trained",
            "platform",
            "infrastructure",
            "hardware",
            "regulated",
            "compliance",
        ]
    )

    if has_infra and (proprietary_signals or has_clients or is_large):
        return (
            "low",
            f"Domain-specific focus ({', '.join(set(focuses) & infra_focuses)}) with proprietary tech or established customer base provides moat against foundation model commoditization.",
        )
    if has_infra:
        return (
            "medium",
            f"Vertical focus ({', '.join(set(focuses) & infra_focuses)}) offers some protection, but limited scale or proprietary differentiation signals.",
        )
    if btype == "consulting":
        if is_large:
            return (
                "medium",
                "Consulting model is vulnerable to AI automation of services, but scale and client relationships provide buffer.",
            )
        return (
            "high",
            "Consulting/services model is highly vulnerable as AI tools enable clients to do work in-house.",
        )
    if has_wrapper and not proprietary_signals and not has_clients:
        return (
            "high",
            f"Focus on {', '.join(set(focuses) & wrapper_focuses)} without clear proprietary tech or established customer base. Foundation models are rapidly commoditizing this space.",
        )
    if has_wrapper and (proprietary_signals or has_clients):
        return (
            "medium",
            f"Works in commoditizing space ({', '.join(set(focuses) & wrapper_focuses)}) but has some differentiation through proprietary tech or customer base.",
        )
    if btype == "enterprise_vendor" or ctype == "enterprise":
        return (
            "low",
            "Enterprise vendor with established market position and switching costs.",
        )
    return (
        "medium",
        "Mixed signals — some differentiation but unclear long-term moat against foundation model capabilities.",
    )


def assess_market_risk(d):
    ctype = d.get("classification", {}).get("company_type", "")
    emp = d.get("size", {}).get("employees_range", "")
    clients = d.get("recognition", {}).get("notable_clients") or []
    customer_count = d.get("recognition", {}).get("customer_count")
    revenue = d.get("financials", {}).get("revenue_estimate_usd")

    if ctype in ("research_lab", "nonprofit"):
        return (
            "not_applicable",
            "Research/nonprofit — not subject to commercial market risk.",
        )

    has_revenue = revenue is not None
    has_customers = len(clients) >= 2 or (customer_count and customer_count > 10)
    is_tiny = emp in ("1-10",)
    is_small = emp in ("1-10", "11-50")

    if has_revenue or (has_customers and not is_tiny):
        return "low", "Established customer base with proven market demand."
    if has_customers:
        return (
            "medium",
            "Some customer traction but still early-stage market validation.",
        )
    if is_small and not has_customers:
        return (
            "high",
            "Small team with no visible customer traction or market validation signals.",
        )
    return "medium", "Limited public information on market traction."


def assess_funding_risk(d):
    ctype = d.get("classification", {}).get("company_type", "")
    emp = d.get("size", {}).get("employees_range", "")
    funding = d.get("financials", {}).get("funding_rounds") or []
    funding_total = d.get("financials", {}).get("funding_total_usd")
    revenue = d.get("financials", {}).get("revenue_estimate_usd")
    publicly_traded = d.get("financials", {}).get("publicly_traded")
    parent = d.get("financials", {}).get("parent_company")

    if ctype in ("research_lab", "nonprofit"):
        return (
            "not_applicable",
            "Research/nonprofit — funded by grants, not venture capital.",
        )
    if ctype == "acquired" or parent:
        return (
            "not_applicable",
            f"Acquired by {parent or 'parent company'} — funded by parent entity.",
        )
    if ctype == "enterprise" or publicly_traded:
        return "low", "Established enterprise/public company with sustainable funding."

    has_significant_funding = funding_total and funding_total > 5_000_000
    has_series = any("series" in (r.get("type", "").lower()) for r in funding)
    has_revenue = revenue is not None
    is_tiny = emp in ("1-10",)

    if has_significant_funding or has_series:
        return (
            "low",
            f"Well-funded with {len(funding)} known funding round(s). Has runway for continued operations.",
        )
    if has_revenue:
        return (
            "low",
            "Revenue-generating — has path to sustainability regardless of external funding.",
        )
    if funding:
        return (
            "medium",
            "Some funding secured but early stage — sustainability depends on continued fundraising or reaching profitability.",
        )
    if is_tiny:
        return (
            "high",
            "No known funding and very small team. High dependency on bootstrapped revenue or future fundraising.",
        )
    return "medium", "No public funding information. Sustainability unclear."


def assess_overall(agi, market, funding):
    levels = {"high": 3, "medium": 2, "low": 1, "not_applicable": 0}
    scores = []
    for risk in [agi, market, funding]:
        if risk != "not_applicable":
            scores.append(levels[risk])

    if not scores:
        return (
            "not_applicable",
            "All risk categories not applicable (research/nonprofit entity).",
        )

    avg = sum(scores) / len(scores)
    if avg >= 2.5:
        return (
            "high",
            "Multiple high-risk factors across AGI displacement, market, or funding dimensions.",
        )
    if avg >= 1.5:
        return (
            "medium",
            "Mixed risk profile — some protective factors but also significant vulnerabilities.",
        )
    return (
        "low",
        "Strong position across assessed risk dimensions with clear moats or stability factors.",
    )


def backfill(path):
    with open(path) as f:
        d = json.load(f)

    if d.get("risk_assessment", {}).get("overall_risk"):
        return False, "already has risk_assessment"

    agi, agi_r = assess_agi_displacement(d)
    market, market_r = assess_market_risk(d)
    funding, funding_r = assess_funding_risk(d)
    overall, overall_r = assess_overall(agi, market, funding)

    d["risk_assessment"] = {
        "agi_displacement": agi,
        "agi_displacement_rationale": agi_r,
        "market_risk": market,
        "market_risk_rationale": market_r,
        "funding_risk": funding,
        "funding_risk_rationale": funding_r,
        "overall_risk": overall,
        "overall_risk_rationale": overall_r,
    }

    with open(path, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return True, f"agi={agi} market={market} funding={funding} overall={overall}"


if __name__ == "__main__":
    paths = []
    for arg in sys.argv[1:]:
        paths.extend(glob.glob(arg))

    updated = 0
    for p in sorted(paths):
        changed, detail = backfill(p)
        name = p.split("/")[-1].replace(".json", "")
        tag = "UPDATED" if changed else "SKIP"
        print(f"  [{tag:7s}] {name:25s} {detail}")
        if changed:
            updated += 1

    print(f"\nUpdated: {updated}/{len(paths)}")
