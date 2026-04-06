from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None


class PendingItem(BaseModel):
    id: int
    sender: str
    subject: str
    status: str
    risk_level: str
    created_at: datetime


class PendingListData(BaseModel):
    items: list[PendingItem]
    total: int
    page: int
    size: int


class EmailDetailData(BaseModel):
    id: int
    sender: str
    recipients: str
    subject: str
    body_text: str
    ai_result: dict | None
    structured_data: dict | None
    draft_reply: str | None
    status: str
    risk_level: str
    erp_sync_status: str
    last_error: str | None
    created_at: datetime


class ApproveRequest(BaseModel):
    operator: str = "cs_agent"
    remark: str = ""


class EditSendRequest(BaseModel):
    operator: str = "cs_agent"
    edited_draft: str = Field(min_length=1)
    remark: str = ""


class RegenerateRequest(BaseModel):
    operator: str = "cs_agent"
    reason: str = ""


class RiskMarkRequest(BaseModel):
    operator: str = "cs_agent"
    level: str = Field(default="HIGH", pattern="^(HIGH|MANUAL)$")
    remark: str = ""
