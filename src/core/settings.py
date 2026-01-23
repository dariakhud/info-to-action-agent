from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CustomBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class Settings(CustomBaseSettings):
    GOOGLE_API_KEY: str
    GOOGLE_GENAI_USE_VERTEXAI: str = Field(default="0")
    LOG_LEVEL: str = Field(default="INFO")  # DEBUG, INFO, WARNING, ERROR, CRITICAL


settings = Settings()
