from __future__ import annotations

import json
from typing import Any

from sqlalchemy import create_engine, text


class DB:
    def __init__(self, dsn: str):
        self.engine = create_engine(dsn, pool_pre_ping=True)

    def save_raw_mail(self, row: dict[str, Any]) -> None:
        sql = text(
            """
            INSERT INTO raw_emails
              (store_id, message_id, thread_id, subject, sender, recipient, sent_at, raw_body, html_body)
            VALUES
              (:store_id, :message_id, :thread_id, :subject, :sender, :recipient, :sent_at, :raw_body, :html_body)
            ON DUPLICATE KEY UPDATE
              subject=VALUES(subject), raw_body=VALUES(raw_body), html_body=VALUES(html_body)
            """
        )
        with self.engine.begin() as conn:
            conn.execute(sql, row)

    def is_processed(self, store_id: str, message_id: str) -> bool:
        sql = text(
            "SELECT 1 FROM processed_email_records WHERE store_id=:store_id AND message_id=:message_id LIMIT 1"
        )
        with self.engine.begin() as conn:
            res = conn.execute(sql, {"store_id": store_id, "message_id": message_id}).scalar()
            return bool(res)

    def save_processed(self, row: dict[str, Any]) -> None:
        sql = text(
            """
            INSERT INTO processed_email_records
            (store_id, message_id, thread_id, payload_json)
            VALUES
            (:store_id, :message_id, :thread_id, :payload_json)
            ON DUPLICATE KEY UPDATE
            payload_json=VALUES(payload_json), thread_id=VALUES(thread_id)
            """
        )
        with self.engine.begin() as conn:
            conn.execute(
                sql,
                {
                    "store_id": row["store_id"],
                    "message_id": row["message_id"],
                    "thread_id": row["thread_id"],
                    "payload_json": json.dumps(row, ensure_ascii=False),
                },
            )
