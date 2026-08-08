# -*- coding: utf-8 -*-
"""应用配置。"""
from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "VibeCoding"
    debug: bool = True
    secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    default_password: str = "Passw0rd!"

    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "vibecoding"

    obs_access_key_id: str = ""
    obs_secret_access_key: str = ""
    obs_endpoint: str = "obs.cn-south-1.myhuaweicloud.com"
    obs_bucket_name: str = "zs-wiki"

    smtp_username: str = ""
    smtp_password: str = ""
    smtp_host: str = "smtp.qq.com"
    smtp_port: int = 587
    smtp_from_name: str = "VibeCoding"

    email_code_expire_minutes: int = 10
    email_code_cooldown_seconds: int = 60

    @property
    def db_url(self) -> str:
        password = quote_plus(self.db_password)
        return (
            f"mysql://{self.db_user}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()

TORTOISE_ORM = {
    "connections": {"default": settings.db_url},
    "apps": {
        "models": {
            "models": ["app.models"],
            "default_connection": "default",
        }
    },
}
