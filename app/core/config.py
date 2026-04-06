from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """统一配置入口：全部来自 .env。"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Codex Email Rules API"
    app_env: str = "dev"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "root"
    mysql_db: str = "email_rules"
    mysql_pool_size: int = 10
    mysql_max_overflow: int = 20

    imap_host: str = "imap.example.com"
    imap_port: int = 993
    imap_user: str = "bot@example.com"
    imap_password: str = "password"
    imap_folder: str = "INBOX"

    smtp_host: str = "smtp.example.com"
    smtp_port: int = 465
    smtp_user: str = "bot@example.com"
    smtp_password: str = "password"
    smtp_use_ssl: bool = True

    ai_provider: str = "mock"
    ai_api_key: str = ""
    ai_base_url: str = ""

    erp_base_url: str = "https://erp.example.com/api"
    erp_api_key: str = ""
    erp_timeout_seconds: int = 15

    poll_interval_seconds: int = Field(default=120, ge=30)

    @property
    def mysql_dsn(self) -> str:
        return (
            f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}?charset=utf8mb4"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
