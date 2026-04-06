import asyncio
import logging
import re

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.db.crud import EmailCRUD
from app.db.session import SessionLocal
from app.services.ai_processor import AIProcessor
from app.services.email_client import IMAPCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class EmailPoller:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.collector = IMAPCollector()
        self.ai = AIProcessor()

    def start(self) -> None:
        self.scheduler.add_job(self.run_once, "interval", seconds=settings.poll_interval_seconds, max_instances=1)
        self.scheduler.start()
        logger.info("Email poller started. interval=%s seconds", settings.poll_interval_seconds)

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    async def run_once(self) -> None:
        logger.info("Email poller tick")
        raw_mails = await asyncio.to_thread(self.collector.fetch_latest)
        async with SessionLocal() as session:
            for mail in raw_mails:
                exists = await EmailCRUD.get_by_message_id(session, mail["message_id"])
                if exists:
                    continue

                cleaned = self._clean_text(mail["body_text"])
                ai_result = await self.ai.analyze(cleaned)
                record_data = {
                    **mail,
                    "cleaned_text": cleaned,
                    "ai_result": ai_result,
                    "structured_data": ai_result.get("structured_data"),
                    "draft_reply": ai_result.get("draft_reply"),
                }
                try:
                    await EmailCRUD.create(session, record_data)
                    await session.commit()
                except IntegrityError:
                    await session.rollback()
                    logger.warning("Duplicate message_id=%s", mail["message_id"])
                except Exception as exc:
                    await session.rollback()
                    logger.exception("Poller write failed: %s", exc)

    @staticmethod
    def _clean_text(text: str) -> str:
        text = re.sub(r"\s+", " ", text).strip()
        return text[:10000]
