from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class RawMail:
    store_id: str
    message_id: str
    thread_id: str
    subject: str
    sender: str
    recipient: str
    sent_at: datetime
    raw_body: str
    html_body: str | None = None


@dataclass
class ProcessedMail:
    store_id: str
    message_id: str
    thread_id: str
    subject: str
    sender: str
    recipient: str
    sent_at: str
    cleaned_body: str
    masked_body: str
    classification: dict[str, Any]
    priority: dict[str, Any]
    rag: dict[str, Any]
    draft_reply: str
    risks: dict[str, Any]
    need_human_review: bool
    review_reason: list[str] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        return asdict(self)
