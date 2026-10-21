from __future__ import annotations

from urllib.parse import urlparse


ALLOWED_SOURCE_TYPES = {"guideline", "knowledge_base", "web", "case_memory"}
ALLOWED_WEB_DOMAINS = {
    "who.int",
    "www.who.int",
    "cdc.gov",
    "www.cdc.gov",
    "nih.gov",
    "www.nih.gov",
    "medlineplus.gov",
    "www.medlineplus.gov",
}
DENYLIST_HINTS = ("forum", "bbs", "tieba", "blog", "营销", "广告", "小红书", "reddit")


def check_required_citations(
    *,
    required_classes: list[str],
    provided_classes: list[str],
    allow_safe_close: bool,
) -> dict[str, object]:
    if allow_safe_close:
        return {"valid": True, "missing": [], "severity": "none"}

    provided = set(provided_classes)
    missing = [citation_class for citation_class in required_classes if citation_class not in provided]
    return {
        "valid": len(missing) == 0,
        "missing": missing,
        "severity": "medium" if missing else "none",
    }


def validate_evidence_sources(
    evidence_items: list[dict[str, str]],
) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    for item in evidence_items:
        source_type = str(item.get("source_type") or "")
        title = str(item.get("title") or "")
        url = str(item.get("url") or "")
        lowered = f"{title} {url}".lower()

        if source_type not in ALLOWED_SOURCE_TYPES:
            violations.append(
                {
                    "rule_id": "evidence_source_type_not_allowed",
                    "severity": "medium",
                    "message": f"Unsupported source type: {source_type}",
                }
            )
            continue

        if any(hint in lowered for hint in DENYLIST_HINTS):
            violations.append(
                {
                    "rule_id": "evidence_source_denylist",
                    "severity": "high",
                    "message": "Evidence source is denylisted.",
                }
            )
            continue

        if source_type == "web" and url:
            domain = urlparse(url).netloc.lower()
            if domain and domain not in ALLOWED_WEB_DOMAINS:
                violations.append(
                    {
                        "rule_id": "evidence_source_allowlist_miss",
                        "severity": "medium",
                        "message": f"Web domain not in allowlist: {domain}",
                    }
                )
    return violations
