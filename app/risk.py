from __future__ import annotations


def detect_risk(text: str, rules: dict) -> dict:
    risk_patterns = rules.get("risk_patterns", {})
    flags = {}
    for name, words in risk_patterns.items():
        flags[name] = any(w.lower() in text.lower() for w in words)
    return {
        "flags": flags,
        "has_risk": any(flags.values()),
    }
