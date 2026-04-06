from __future__ import annotations

import email
import imaplib
from datetime import datetime
from email.header import decode_header
from email.utils import parsedate_to_datetime

from app.config import StoreConfig
from app.models import RawMail


def _decode(v: str | None) -> str:
    if not v:
        return ""
    parts = decode_header(v)
    out = []
    for raw, enc in parts:
        if isinstance(raw, bytes):
            out.append(raw.decode(enc or "utf-8", errors="ignore"))
        else:
            out.append(raw)
    return "".join(out)


def _extract_body(msg: email.message.Message) -> tuple[str, str | None]:
    text_body = ""
    html_body = None
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get("Content-Disposition", ""))
            if "attachment" in disp:
                continue
            payload = part.get_payload(decode=True)
            if payload is None:
                continue
            charset = part.get_content_charset() or "utf-8"
            content = payload.decode(charset, errors="ignore")
            if ctype == "text/plain" and not text_body:
                text_body = content
            elif ctype == "text/html" and html_body is None:
                html_body = content
    else:
        payload = msg.get_payload(decode=True) or b""
        charset = msg.get_content_charset() or "utf-8"
        text_body = payload.decode(charset, errors="ignore")
    return text_body, html_body


def fetch_unseen(store: StoreConfig, limit: int = 50) -> list[RawMail]:
    mails: list[RawMail] = []
    client = imaplib.IMAP4_SSL(store.imap_host, store.imap_port)
    client.login(store.email, store.password)
    client.select(store.folder)
    status, data = client.search(None, "UNSEEN")
    if status != "OK":
        client.logout()
        return mails

    ids = data[0].split()[-limit:]
    for email_id in ids:
        st, msg_data = client.fetch(email_id, "(RFC822)")
        if st != "OK":
            continue
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)

        message_id = msg.get("Message-ID", "").strip("<>")
        references = msg.get("References") or msg.get("In-Reply-To") or message_id
        subject = _decode(msg.get("Subject"))
        sender = _decode(msg.get("From"))
        recipient = _decode(msg.get("To"))
        sent_at_raw = msg.get("Date")
        sent_at = parsedate_to_datetime(sent_at_raw) if sent_at_raw else datetime.utcnow()
        text_body, html_body = _extract_body(msg)

        mails.append(
            RawMail(
                store_id=store.store_id,
                message_id=message_id,
                thread_id=references,
                subject=subject,
                sender=sender,
                recipient=recipient,
                sent_at=sent_at,
                raw_body=text_body,
                html_body=html_body,
            )
        )

    client.logout()
    return mails
