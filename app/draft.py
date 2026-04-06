from __future__ import annotations

from app.llm_client import LLMClient


def generate_reply_draft(
    llm: LLMClient,
    subject: str,
    body: str,
    classification: dict,
    rag: dict,
    rules: dict,
) -> str:
    prompt = (
        f"你是店铺客服。分类={classification}.\n"
        f"邮件主题={subject}\n"
        f"用户内容={body}\n"
        f"知识库命中={rag.get('hits', [])}\n"
        f"必须遵守合规规则={rules.get('compliance', [])}\n"
        "输出 JSON: {draft_reply: string}"
    )
    res = llm.json_chat("你是合规客服回复生成器", prompt)
    return res.get("draft_reply", "")
