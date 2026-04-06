from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import EmailRecord, ReviewAction, ReviewStatus


class EmailCRUD:
    @staticmethod
    async def list_pending(session: AsyncSession, page: int, size: int) -> tuple[list[EmailRecord], int]:
        stmt = (
            select(EmailRecord)
            .where(EmailRecord.status.in_([ReviewStatus.pending, ReviewStatus.regenerated]))
            .order_by(desc(EmailRecord.created_at))
            .offset((page - 1) * size)
            .limit(size)
        )
        total_stmt = select(EmailRecord).where(
            EmailRecord.status.in_([ReviewStatus.pending, ReviewStatus.regenerated])
        )
        items = (await session.scalars(stmt)).all()
        total = len((await session.scalars(total_stmt)).all())
        return items, total

    @staticmethod
    async def get_by_id(session: AsyncSession, email_id: int) -> EmailRecord | None:
        return await session.get(EmailRecord, email_id)

    @staticmethod
    async def get_by_message_id(session: AsyncSession, message_id: str) -> EmailRecord | None:
        stmt = select(EmailRecord).where(EmailRecord.message_id == message_id)
        return (await session.scalars(stmt)).first()

    @staticmethod
    async def create(session: AsyncSession, data: dict) -> EmailRecord:
        obj = EmailRecord(**data)
        session.add(obj)
        await session.flush()
        return obj

    @staticmethod
    async def update(session: AsyncSession, email: EmailRecord, fields: dict) -> EmailRecord:
        for key, value in fields.items():
            setattr(email, key, value)
        await session.flush()
        return email


class ActionCRUD:
    @staticmethod
    async def create(session: AsyncSession, email_id: int, action: str, operator: str, remark: str = "", payload=None):
        log = ReviewAction(email_id=email_id, action=action, operator=operator, remark=remark, payload=payload)
        session.add(log)
        await session.flush()
        return log
