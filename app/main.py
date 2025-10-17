from fastapi import FastAPI
from app.core.logging import setup_logging
from app.api.errors import register_exception_handlers
from app.api.routers import health, cars, policies, claims
import app.api.routers.history as history  # <- explicit

setup_logging()
app = FastAPI(title="Car Insurance API")
register_exception_handlers(app)

app.include_router(health.router)
app.include_router(cars.router)
app.include_router(policies.router)
app.include_router(claims.router)
app.include_router(history.router)  # <- must be present

