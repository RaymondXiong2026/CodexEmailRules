from __future__ import annotations

from app.llm_client import LLMClient


def classify_email(llm: LLMClient, rules: dict, subject: str, body: str) -> dict:
    categories = rules.get("categories", [])
    prompt = (
        "请基于规则给出一级分类、二级分类、置信度(0-1)。"
        f"候选分类: {categories}\n"
        f"Subject: {subject}\nBody:{body}"
    )
    return llm.json_chat(
        "你是电商邮件分类引擎，只输出 JSON：{primary, secondary, confidence, reason}",
        prompt,
    )
