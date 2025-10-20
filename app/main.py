from fastapi import FastAPI
from app.core.logging import setup_logging
from app.core.config import settings
from app.core.scheduling import start_scheduler, shutdown_scheduler
from app.api.errors import register_exception_handlers
from app.api.routers import health, cars, policies, claims, history
from app.api.middleware import RequestIDMiddleware


setup_logging()
app = FastAPI(title="Car Insurance API")
register_exception_handlers(app)


# Routers
app.include_router(health.router)
app.include_router(cars.router)
app.include_router(policies.router)
app.include_router(claims.router)
app.include_router(history.router)

app.add_middleware(RequestIDMiddleware)


@app.on_event("startup")
async def _startup():
    if settings.SCHEDULER_ENABLED:
        start_scheduler()


@app.on_event("shutdown")
async def _shutdown():
    if settings.SCHEDULER_ENABLED:
        shutdown_scheduler()
