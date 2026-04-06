from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, DateTime, Enum as SqlEnum, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReviewStatus(str, Enum):
    pending = "PENDING"
    approved = "APPROVED"
    sent = "SENT"
    regenerated = "REGENERATED"
    high_risk = "HIGH_RISK"
    manual = "MANUAL"


class EmailRecord(Base):
    __tablename__ = "email_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, comment="邮件唯一ID")
    sender: Mapped[str] = mapped_column(String(255), index=True, comment="发件人")
    recipients: Mapped[str] = mapped_column(Text, comment="收件人列表，逗号分隔")
    subject: Mapped[str] = mapped_column(String(500), index=True, comment="邮件主题")
    body_text: Mapped[str] = mapped_column(Text, comment="邮件原文")
    cleaned_text: Mapped[str | None] = mapped_column(Text, nullable=True, comment="清洗后文本")
    ai_result: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="AI分析原始结果")
    structured_data: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="结构化业务数据")
    draft_reply: Mapped[str | None] = mapped_column(Text, nullable=True, comment="AI草稿")
    status: Mapped[ReviewStatus] = mapped_column(
        SqlEnum(ReviewStatus), default=ReviewStatus.pending, index=True, comment="审核状态"
    )
    risk_level: Mapped[str] = mapped_column(String(20), default="LOW", index=True, comment="风险等级")
    erp_sync_status: Mapped[str] = mapped_column(String(20), default="PENDING", comment="ERP同步状态")
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True, comment="最近一次错误")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class ReviewAction(Base):
    __tablename__ = "review_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email_id: Mapped[int] = mapped_column(Integer, index=True, comment="邮件ID")
    action: Mapped[str] = mapped_column(String(50), index=True, comment="操作类型")
    operator: Mapped[str] = mapped_column(String(100), default="system", comment="操作人")
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="附加数据")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
