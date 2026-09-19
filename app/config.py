"""
Application configuration.

All configurable values (database URL, allowed CORS origins, etc.) are
read from environment variables instead of being hard-coded. This means
no secrets ever live in the source code, and the same code can be run
against different databases/environments just by changing the .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Default value below is only used if DATABASE_URL is not set at all.
    # In real usage this should always come from the .env file.
    database_url: str = (
        "postgresql://postgres:postgres@localhost:5432/student_registration"
    )

    # Comma-separated origins allowed to call this API.
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
