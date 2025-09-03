from typing import Final

from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


class SSOSettings(BaseSettings):
    base_url: str = "http://localhost:8000/api/v1"
    realm: str = "messenger"

    model_config = SettingsConfigDict(env_prefix="SSO_")


class Settings(BaseSettings):
    sso: SSOSettings = SSOSettings()


settings: Final[Settings] = Settings()
