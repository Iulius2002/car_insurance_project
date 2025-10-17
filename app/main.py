from fastapi import FastAPI
from app.core.logging import setup_logging
from app.api.routers import health, cars, policies # add policies here
from app.api.errors import register_exception_handlers
from app.api.routers import health, cars, policies, claims # add claims


setup_logging()
app = FastAPI(title="Car Insurance API")
register_exception_handlers(app)


# Routers
app.include_router(health.router)
app.include_router(cars.router)
app.include_router(policies.router) # ensure this line exists
app.include_router(claims.router)