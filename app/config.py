"""
Application configuration.

All configurable values (database URL, allowed CORS origins, etc.) are
read from environment variables instead of being hard-coded. This means
no secrets ever live in the source code, and the same code can be run
against different databases/environments just by changing the .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = (
        "postgresql://postgres:postgres@localhost:5432/student_registration"
    )

    cors_origins: str = "http://localhost:3000"

    # JWT / admin auth settings
    jwt_secret_key: str = "CHANGE_ME_dev_only_secret_key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    auth_cookie_name: str = "access_token"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
