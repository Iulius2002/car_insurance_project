from fastapi import FastAPI
from app.core.logging import setup_logging
from app.api.routers import health, cars


setup_logging()
app = FastAPI(title="Car Insurance API")


# Routers
app.include_router(health.router)
app.include_router(cars.router)