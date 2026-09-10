import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        # PyInstaller guarda los recursos en _MEIPASS
        return Path(sys._MEIPASS)
    
    # Modo desarrollo (Python normal)
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    TENANT_ID: str = Field(default="")
    BASE_DIR: Path = BASE_DIR
    CLIENT_ID: str = Field(default="")
    CLIENT_SECRET: str = Field(default="")
    SENDER_EMAIL: str = Field(default="")

    GITHUB_TOKEN: str = Field(default="")
    GITHUB_USER: str = Field(default="")
    GITHUB_REPO: str = Field(default="")
    URL: str = Field(default="")
    ACCOUNT_SID: str = Field(default="")
    AUTH_TOKEN: str = Field(default="")
    TEMPLATE_SID: str = Field(default="")

    FECHA_ACTUAL: datetime = Field(
        default_factory=lambda: datetime.now(ZoneInfo("America/Mexico_City"))
    )


settings = Settings()