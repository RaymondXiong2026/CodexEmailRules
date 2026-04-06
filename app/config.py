from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


@dataclass
class StoreConfig:
    store_id: str
    email: str
    password: str
    imap_host: str
    imap_port: int
    folder: str = "INBOX"


@dataclass
class AppConfig:
    env: str
    log_level: str
    poll_interval_seconds: int
    mysql_dsn: str
    openai_api_key: str
    openai_base_url: str
    openai_model: str
    openai_timeout: int
    stores: list[StoreConfig]
    workflow_rules: dict[str, Any]


def _load_rules(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"workflow rules file not found: {path}")
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_config() -> AppConfig:
    load_dotenv()
    stores_raw = os.getenv("IMAP_STORES_JSON", "[]")
    stores_data = json.loads(stores_raw)
    stores = [StoreConfig(**s) for s in stores_data]
    mysql_dsn = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
        f"@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
        "?charset=utf8mb4"
    )
    rules_path = os.getenv("WORKFLOW_RULES_PATH", "config/workflow_rules.yaml")

    return AppConfig(
        env=os.getenv("APP_ENV", "dev"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        poll_interval_seconds=int(os.getenv("POLL_INTERVAL_SECONDS", "60")),
        mysql_dsn=mysql_dsn,
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        openai_timeout=int(os.getenv("OPENAI_TIMEOUT", "30")),
        stores=stores,
        workflow_rules=_load_rules(rules_path),
    )
