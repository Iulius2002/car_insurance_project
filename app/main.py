from fastapi import FastAPI
from app.core.logging import setup_logging
from app.api.routers import health


setup_logging()
app = FastAPI(title="Car Insurance API")
app.include_router(health.router)