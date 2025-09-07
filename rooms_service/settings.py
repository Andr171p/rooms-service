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


class PostgresSettings(BaseSettings):
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "password"
    db: str = "postgres"
    driver: str = "asyncpg"

    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    @property
    def sqlalchemy_url(self) -> str:
        return f"postgresql+{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class Settings(BaseSettings):
    sso: SSOSettings = SSOSettings()
    postgres: PostgresSettings = PostgresSettings()


settings: Final[Settings] = Settings()
