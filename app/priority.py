from __future__ import annotations


def decide_priority(classification: dict, rules: dict) -> dict:
    pri_rules = rules.get("priority", {})
    primary = classification.get("primary", "")
    confidence = float(classification.get("confidence", 0))
    cfg = pri_rules.get(primary, pri_rules.get("default", {"priority": "P2", "sla_hours": 24}))

    if confidence < rules.get("thresholds", {}).get("low_confidence", 0.6):
        return {"priority": "P1", "sla_hours": 4, "reason": "low_confidence"}

    return {
        "priority": cfg.get("priority", "P2"),
        "sla_hours": cfg.get("sla_hours", 24),
        "reason": cfg.get("reason", "rule_match"),
    }
