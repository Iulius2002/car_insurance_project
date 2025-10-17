from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+pysqlite:///./dev.db"
    SCHEDULER_ENABLED: bool = False
    SCHEDULER_TEST_MODE: bool = False
    LOG_LEVEL: str = "DEBUG"

    # .env support; keep case-sensitive so keys must match exactly
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
