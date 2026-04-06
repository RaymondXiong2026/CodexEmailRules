import email
import imaplib
from email.header import decode_header

from app.core.config import get_settings

settings = get_settings()


class IMAPCollector:
    """从 IMAP 拉取邮件，返回标准结构。"""

    def fetch_latest(self, limit: int = 20) -> list[dict]:
        results: list[dict] = []
        with imaplib.IMAP4_SSL(settings.imap_host, settings.imap_port) as m:
            m.login(settings.imap_user, settings.imap_password)
            m.select(settings.imap_folder)
            status, data = m.search(None, "ALL")
            if status != "OK":
                return results

            ids = data[0].split()[-limit:]
            for mid in ids:
                _, msg_data = m.fetch(mid, "(RFC822)")
                raw = msg_data[0][1]
                parsed = email.message_from_bytes(raw)
                message_id = parsed.get("Message-ID", f"imap-{mid.decode()}")
                sender = parsed.get("From", "")
                subject = self._decode_value(parsed.get("Subject", ""))
                body = self._extract_body(parsed)
                results.append(
                    {
                        "message_id": message_id,
                        "sender": sender,
                        "recipients": settings.imap_user,
                        "subject": subject,
                        "body_text": body,
                    }
                )
        return results

    @staticmethod
    def _decode_value(value: str) -> str:
        decoded = decode_header(value)
        text = ""
        for chunk, enc in decoded:
            if isinstance(chunk, bytes):
                text += chunk.decode(enc or "utf-8", errors="ignore")
            else:
                text += chunk
        return text

    @staticmethod
    def _extract_body(parsed) -> str:
        if parsed.is_multipart():
            for part in parsed.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain" and "attachment" not in str(part.get("Content-Disposition")):
                    payload = part.get_payload(decode=True)
                    if payload:
                        return payload.decode(part.get_content_charset() or "utf-8", errors="ignore")
        payload = parsed.get_payload(decode=True)
        return (payload or b"").decode(parsed.get_content_charset() or "utf-8", errors="ignore")
