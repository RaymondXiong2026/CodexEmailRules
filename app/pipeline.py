from __future__ import annotations

import logging
from datetime import datetime

from app.classification import classify_email
from app.config import AppConfig
from app.db import DB
from app.draft import generate_reply_draft
from app.imap_client import fetch_unseen
from app.llm_client import LLMClient
from app.models import ProcessedMail
from app.priority import decide_priority
from app.rag import HybridRAG, KBItem
from app.review import need_manual_review
from app.risk import detect_risk
from app.text_processing import clean_body, mask_pii

logger = logging.getLogger(__name__)


def _load_kb(cfg: AppConfig) -> list[KBItem]:
    items = cfg.workflow_rules.get("knowledge_base", [])
    return [KBItem(**it) for it in items]


def run_once(cfg: AppConfig) -> None:
    db = DB(cfg.mysql_dsn)
    llm = LLMClient(cfg.openai_api_key, cfg.openai_base_url, cfg.openai_model, cfg.openai_timeout)
    rag_engine = HybridRAG(_load_kb(cfg))

    for store in cfg.stores:
        logger.info("polling store=%s", store.store_id)
        mails = fetch_unseen(store)
        for m in mails:
            if not m.message_id:
                logger.warning("skip message without message-id, store=%s", store.store_id)
                continue
            if db.is_processed(m.store_id, m.message_id):
                logger.info("skip duplicated processed mail %s", m.message_id)
                continue

            db.save_raw_mail(
                {
                    "store_id": m.store_id,
                    "message_id": m.message_id,
                    "thread_id": m.thread_id,
                    "subject": m.subject,
                    "sender": m.sender,
                    "recipient": m.recipient,
                    "sent_at": m.sent_at,
                    "raw_body": m.raw_body,
                    "html_body": m.html_body,
                }
            )

            cleaned = clean_body(m.raw_body)
            masked = mask_pii(cleaned)
            cls = classify_email(llm, cfg.workflow_rules, m.subject, masked)
            priority = decide_priority(cls, cfg.workflow_rules)
            rag = rag_engine.search(m.store_id, cls.get("primary", ""), masked)
            risk = detect_risk(masked, cfg.workflow_rules)
            draft = generate_reply_draft(llm, m.subject, masked, cls, rag, cfg.workflow_rules)
            review, reasons = need_manual_review(cls, risk, rag, cfg.workflow_rules)

            record = ProcessedMail(
                store_id=m.store_id,
                message_id=m.message_id,
                thread_id=m.thread_id,
                subject=m.subject,
                sender=m.sender,
                recipient=m.recipient,
                sent_at=m.sent_at.isoformat() if isinstance(m.sent_at, datetime) else str(m.sent_at),
                cleaned_body=cleaned,
                masked_body=masked,
                classification=cls,
                priority=priority,
                rag=rag,
                draft_reply=draft,
                risks=risk,
                need_human_review=review,
                review_reason=reasons,
            ).to_json()

            db.save_processed(record)
            logger.info("processed store=%s msg=%s", m.store_id, m.message_id)
