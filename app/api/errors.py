from fastapi import Request
from fastapi.responses import JSONResponse
import structlog

log = structlog.get_logger()

class CarNotFoundError(Exception):
    def __init__(self, car_id: int):
        self.car_id = car_id

class BadRequestError(Exception):
    def __init__(self, detail: str):
        self.detail = detail

def register_exception_handlers(app):
    @app.exception_handler(CarNotFoundError)
    async def car_not_found_handler(request: Request, exc: CarNotFoundError):
        log.warning("car_not_found", carId=exc.car_id)
        return JSONResponse(status_code=404, content={"detail": "Car not found"})

    @app.exception_handler(BadRequestError)
    async def bad_request_handler(request: Request, exc: BadRequestError):
        log.info("bad_request", detail=exc.detail)
        return JSONResponse(status_code=400, content={"detail": exc.detail})