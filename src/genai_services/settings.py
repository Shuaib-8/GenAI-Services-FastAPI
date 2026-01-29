from pathlib import Path
from typing import Annotated

from pydantic import Field, HttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")

    port: Annotated[int, Field(default=8000)]
    app_secret: Annotated[str, Field(min_length=32)]
    pg_dsn: Annotated[
        PostgresDsn,
        Field(
            alias="DATABASE_URL",
            default="postgresql://user:password@localhost:5432/database",
        ),
    ]
    cors_whitelist: Annotated[
        set[HttpUrl],
        Field(alias="CORS_WHITELIST", default=["http://localhost:3000"]),
    ]
    # check follows sk-proj-...: can define in .env or as a global environment variable
    openai_api_key: Annotated[
        str, Field(alias="OPENAI_API_KEY", pattern=r"^sk-proj-.*$")
    ]
    ollama_api_key: Annotated[str, Field(alias="OLLAMA_API_KEY")]


settings = AppSettings()
