import json
import sys

ENUMS = {
    "classification.business_type": {
        "b2b_saas",
        "b2c_saas",
        "consulting",
        "product",
        "research",
        "enterprise_vendor",
        "other",
    },
    "classification.company_type": {
        "startup",
        "scaleup",
        "enterprise",
        "acquired",
        "research_lab",
        "nonprofit",
    },
    "classification.ai_focus": {
        "nlp",
        "cv",
        "ml_ops",
        "generative_ai",
        "robotics",
        "data_engineering",
        "fraud_detection",
        "recommendation",
        "speech",
        "automation",
        "document_processing",
        "other",
    },
    "size.employees_range": {
        "1-10",
        "11-50",
        "51-200",
        "201-500",
        "501-1000",
        "1001-5000",
        "5000+",
    },
    "financials.business_model": {
        "subscription_saas",
        "usage_based",
        "consulting_services",
        "licensing",
        "marketplace",
        "freemium",
        "other",
    },
    "careers.hiring_signals": {"actively_hiring", "few_roles", "not_hiring", "unknown"},
    "metadata.data_quality": {"high", "medium", "low"},
    "risk_assessment.agi_displacement": {"high", "medium", "low", "not_applicable"},
    "risk_assessment.market_risk": {"high", "medium", "low", "not_applicable"},
    "risk_assessment.funding_risk": {"high", "medium", "low", "not_applicable"},
    "risk_assessment.overall_risk": {"high", "medium", "low", "not_applicable"},
}

REQUIRED = [
    "id",
    "name",
    "category",
    "scraped_at",
    "overview.description",
    "overview.description_long",
    "classification.business_type",
    "classification.company_type",
    "classification.is_ai_native",
    "size.employees_range",
    "financials.publicly_traded",
    "metadata.data_quality",
    "risk_assessment.agi_displacement",
    "risk_assessment.market_risk",
    "risk_assessment.funding_risk",
    "risk_assessment.overall_risk",
]

EMPLOYEE_SNAP = {
    range(1, 11): "1-10",
    range(11, 51): "11-50",
    range(51, 201): "51-200",
    range(201, 501): "201-500",
    range(501, 1001): "501-1000",
    range(1001, 5001): "1001-5000",
    range(5001, 999999): "5000+",
}

AI_FOCUS_MAP = {
    "machine learning": "other",
    "anomaly detection": "fraud_detection",
    "fraud detection": "fraud_detection",
    "computer vision": "cv",
    "natural language processing": "nlp",
    "optimization": "other",
    "document processing": "document_processing",
    "generative ai": "generative_ai",
    "conversational ai": "nlp",
    "ai agents": "automation",
    "contact center automation": "automation",
    "customer experience": "other",
    "digital humans": "generative_ai",
    "voice bots": "speech",
    "chatbots": "nlp",
    "recommendation systems": "recommendation",
    "personalization": "recommendation",
    "collaborative filtering": "recommendation",
    "content-based filtering": "recommendation",
    "reinforcement learning": "other",
    "real-time ai": "other",
    "personalized search": "recommendation",
    "llm-powered features": "generative_ai",
    "applied_ai": "other",
    "predictive_analytics": "other",
    "ai-assisted automation": "automation",
    "web scraping": "data_engineering",
    "data extraction": "data_engineering",
    "browser automation": "automation",
    "cloud infrastructure": "other",
    "ai sandboxes": "other",
    "data operations": "data_engineering",
    "data integration": "data_engineering",
    "etl": "data_engineering",
    "ai for enterprise": "other",
    "customer insight analytics": "other",
    "data science notebooks": "data_engineering",
    "collaborative analytics": "data_engineering",
    "ai-assisted data exploration": "data_engineering",
    "data workspace with ai agents": "data_engineering",
    "ai agent infrastructure": "other",
    "code execution sandboxing": "other",
    "cloud computing for ai": "other",
    "code interpretation": "other",
    "secure computer use": "other",
    "data automation": "data_engineering",
    "ai for finance": "other",
    "data analytics": "data_engineering",
    "workflow automation": "automation",
    "no-code/low-code": "automation",
    "process automation": "automation",
    "integration platform": "data_engineering",
}

BUSINESS_TYPE_MAP = {
    "b2b": "b2b_saas",
    "b2c": "b2c_saas",
    "saas": "b2b_saas",
}

COMPANY_TYPE_MAP = {
    "private": "startup",
    "unicorn": "scaleup",
    "subsidiary": "acquired",
}

BUSINESS_MODEL_MAP = {
    "subscription": "subscription_saas",
    "saas": "subscription_saas",
    "freemium": "freemium",
    "usage-based": "usage_based",
    "consulting": "consulting_services",
    "license": "licensing",
    "marketplace": "marketplace",
}


def get_nested(d, path):
    for k in path.split("."):
        if isinstance(d, dict):
            d = d.get(k)
        else:
            return None
    return d


def set_nested(d, path, val):
    keys = path.split(".")
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = val


def snap_employees(val):
    if val is None:
        return None
    val = str(val).strip()
    if val in ENUMS["size.employees_range"]:
        return val
    try:
        n = int(val.replace("+", "").replace("~", "").split("-")[0])
    except ValueError:
        return None
    for r, label in EMPLOYEE_SNAP.items():
        if n in r:
            return label
    return "5000+"


def validate(path):
    with open(path) as f:
        d = json.load(f)

    errors = []
    fixes = []

    for field in REQUIRED:
        v = get_nested(d, field)
        if v is None:
            errors.append(f"MISSING required: {field}")

    for field, allowed in ENUMS.items():
        v = get_nested(d, field)
        if v is None:
            continue

        if isinstance(v, list):
            new_list = []
            for item in v:
                if item in allowed:
                    new_list.append(item)
                elif field == "classification.ai_focus":
                    mapped = AI_FOCUS_MAP.get(item.lower())
                    if mapped:
                        new_list.append(mapped)
                        fixes.append(f"FIXED {field}: {item} -> {mapped}")
                    else:
                        errors.append(f"BAD enum: {field}={item}")
                        new_list.append(item)
                else:
                    errors.append(f"BAD enum: {field}={item}")
                    new_list.append(item)
            deduped = list(dict.fromkeys(new_list))
            if deduped != v:
                set_nested(d, field, deduped)
            continue

        if v in allowed:
            continue

        normalized = (
            v.lower()
            .strip()
            .split(".")[0]
            .split(",")[0]
            .split("(")[0]
            .strip()
            .replace(" ", "_")
        )
        if normalized in allowed:
            set_nested(d, field, normalized)
            fixes.append(f"FIXED {field}: {v} -> {normalized}")
            continue

        if field == "size.employees_range":
            fixed = snap_employees(v)
            if fixed:
                set_nested(d, field, fixed)
                fixes.append(f"FIXED {field}: {v} -> {fixed}")
            else:
                errors.append(f"BAD enum: {field}={v}")
        elif field == "metadata.data_quality":
            mapping = {
                "good": "medium",
                "moderate": "medium",
                "excellent": "high",
                "poor": "low",
            }
            fixed = mapping.get(v.lower().strip())
            if fixed:
                set_nested(d, field, fixed)
                fixes.append(f"FIXED {field}: {v} -> {fixed}")
            else:
                errors.append(f"BAD enum: {field}={v}")
        elif field == "classification.business_type":
            fixed = BUSINESS_TYPE_MAP.get(normalized) or BUSINESS_TYPE_MAP.get(
                v.lower().strip()
            )
            if fixed:
                set_nested(d, field, fixed)
                fixes.append(f"FIXED {field}: {v} -> {fixed}")
            else:
                errors.append(f"BAD enum: {field}={v}")
        elif field == "classification.company_type":
            fixed = COMPANY_TYPE_MAP.get(normalized) or COMPANY_TYPE_MAP.get(
                v.lower().strip()
            )
            if fixed:
                set_nested(d, field, fixed)
                fixes.append(f"FIXED {field}: {v} -> {fixed}")
            else:
                errors.append(f"BAD enum: {field}={v}")
        elif field == "financials.business_model":
            for key, val in BUSINESS_MODEL_MAP.items():
                if key in v.lower():
                    set_nested(d, field, val)
                    fixes.append(f"FIXED {field}: {v} -> {val}")
                    break
            else:
                errors.append(f"BAD enum: {field}={v}")
        elif field == "careers.hiring_signals":
            low = v.lower()
            if "actively" in low or "hiring" in low or "active" in low:
                set_nested(d, field, "actively_hiring")
                fixes.append(f"FIXED {field}: (long text) -> actively_hiring")
            elif "few" in low:
                set_nested(d, field, "few_roles")
                fixes.append(f"FIXED {field}: (long text) -> few_roles")
            else:
                set_nested(d, field, "unknown")
                fixes.append(f"FIXED {field}: (long text) -> unknown")
        else:
            errors.append(f"BAD enum: {field}={v}")

    if fixes:
        with open(path, "w") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)

    return errors, fixes


def cli():
    if len(sys.argv) < 2:
        print("Usage: validate <path_or_glob>")
        sys.exit(1)

    import glob as g

    paths = []
    for arg in sys.argv[1:]:
        paths.extend(g.glob(arg))

    total_errors = 0
    total_fixes = 0
    for p in sorted(paths):
        errors, fixes = validate(p)
        name = p.split("/")[-1].replace(".json", "")
        status = "OK" if not errors else f"{len(errors)} errors"
        fix_str = f", {len(fixes)} auto-fixed" if fixes else ""
        print(f"  {name:20s} {status}{fix_str}")
        for f in fixes:
            print(f"    {f}")
        for e in errors:
            print(f"    {e}")
        total_errors += len(errors)
        total_fixes += len(fixes)

    print(
        f"\nTotal: {len(paths)} files, {total_errors} errors, {total_fixes} auto-fixes"
    )
    sys.exit(1 if total_errors else 0)


if __name__ == "__main__":
    cli()
