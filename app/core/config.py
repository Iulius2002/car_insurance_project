from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "car-insurance-api"
    LOG_LEVEL: str = "INFO"
    SCHEDULER_ENABLED: bool = False
    # Dev DB placeholder; we’ll override later once DB is added
    DATABASE_URL: str = "sqlite+pysqlite:///./dev.db"


    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)
    SCHEDULER_ENABLED: bool = False
    SCHEDULER_TEST_MODE: bool = False  # when True, runs the expiry check even outside the 00:00–01:00 window (for dev)


settings = Settings()