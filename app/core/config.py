from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "car-insurance-api"
    LOG_LEVEL: str = "INFO"
    SCHEDULER_ENABLED: bool = False
    # Dev DB placeholder; we’ll override later once DB is added
    DATABASE_URL: str = "sqlite+pysqlite:///./dev.db"


    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


settings = Settings()