from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud import ActionCRUD, EmailCRUD
from app.db.models import ReviewStatus
from app.services.ai_processor import AIProcessor
from app.services.erp_client import ERPClient
from app.services.mail_sender import MailSender


class ReviewWorkflow:
    def __init__(self):
        self.mailer = MailSender()
        self.erp = ERPClient()
        self.ai = AIProcessor()

    async def approve_and_execute(self, session: AsyncSession, email_id: int, operator: str, remark: str):
        email = await EmailCRUD.get_by_id(session, email_id)
        if not email:
            return None

        await self.mailer.send(email.sender, email.subject, email.draft_reply or "")
        await self.erp.push(email.structured_data or {})

        await EmailCRUD.update(
            session,
            email,
            {"status": ReviewStatus.sent, "erp_sync_status": "SYNCED", "last_error": None},
        )
        await ActionCRUD.create(session, email_id, "APPROVE_AND_SEND", operator, remark)
        await session.commit()
        return email

    async def send_edited(self, session: AsyncSession, email_id: int, operator: str, edited_draft: str, remark: str):
        email = await EmailCRUD.get_by_id(session, email_id)
        if not email:
            return None

        await self.mailer.send(email.sender, email.subject, edited_draft)
        await self.erp.push(email.structured_data or {})

        await EmailCRUD.update(
            session,
            email,
            {
                "draft_reply": edited_draft,
                "status": ReviewStatus.sent,
                "erp_sync_status": "SYNCED",
                "last_error": None,
            },
        )
        await ActionCRUD.create(session, email_id, "EDIT_AND_SEND", operator, remark, payload={"edited": True})
        await session.commit()
        return email

    async def regenerate(self, session: AsyncSession, email_id: int, operator: str, reason: str):
        email = await EmailCRUD.get_by_id(session, email_id)
        if not email:
            return None

        ai_result = await self.ai.analyze(email.cleaned_text or email.body_text)
        await EmailCRUD.update(
            session,
            email,
            {
                "ai_result": ai_result,
                "structured_data": ai_result.get("structured_data"),
                "draft_reply": ai_result.get("draft_reply"),
                "status": ReviewStatus.regenerated,
            },
        )
        await ActionCRUD.create(session, email_id, "REGENERATE", operator, reason)
        await session.commit()
        return email

    async def mark_risk(self, session: AsyncSession, email_id: int, operator: str, level: str, remark: str):
        email = await EmailCRUD.get_by_id(session, email_id)
        if not email:
            return None

        status = ReviewStatus.high_risk if level == "HIGH" else ReviewStatus.manual
        await EmailCRUD.update(session, email, {"risk_level": level, "status": status})
        await ActionCRUD.create(session, email_id, "MARK_RISK", operator, remark, payload={"level": level})
        await session.commit()
        return email
