from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = ""
    azure_openai_api_version: str = "2024-10-21"
    frontend_origins: str = "http://localhost:5173"
    max_upload_mb: int = Field(default=10, ge=1, le=50)
    max_source_characters: int = Field(default=20_000, ge=1_000, le=100_000)
    enable_development_fallback: bool = False

    @property
    def ai_configured(self) -> bool:
        return all(
            (
                self.azure_openai_endpoint,
                self.azure_openai_api_key,
                self.azure_openai_deployment,
            )
        )

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
