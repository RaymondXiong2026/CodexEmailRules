from __future__ import annotations


def need_manual_review(classification: dict, risk: dict, rag: dict, rules: dict) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    low_conf = rules.get("thresholds", {}).get("low_confidence", 0.6)
    rag_hit = rules.get("thresholds", {}).get("rag_min_score", 0.25)

    if float(classification.get("confidence", 0)) < low_conf:
        reasons.append("low_confidence")
    if risk.get("has_risk", False):
        reasons.append("risk_detected")
    if float(rag.get("score", 0)) < rag_hit:
        reasons.append("low_kb_hit")

    return (len(reasons) > 0, reasons)
