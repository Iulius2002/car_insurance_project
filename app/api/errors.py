from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import structlog


log = structlog.get_logger()


class CarNotFoundError(Exception):
    def __init__(self, car_id: int):
        self.car_id = car_id


class BadRequestError(Exception):
    def __init__(self, detail: str):
        self.detail = detail


def _validation_payload(exc) -> dict:
    """Normalize Pydantic/FastAPI validation errors into a consistent envelope."""
    try:
        errs = exc.errors()
    except Exception:
        errs = []
    return {
        "detail": "Validation error",
        "errors": [
            {
                "loc": e.get("loc", []),
                "msg": e.get("msg", "invalid input"),
                "type": e.get("type", "value_error"),
            }
            for e in errs
        ],
    }


def register_exception_handlers(app):
    @app.exception_handler(CarNotFoundError)
    async def car_not_found_handler(request: Request, exc: CarNotFoundError):
        log.warning("car_not_found", carId=exc.car_id, path=str(request.url))
        return JSONResponse(status_code=404, content={"detail": "Car not found"})

    @app.exception_handler(BadRequestError)
    async def bad_request_handler(request: Request, exc: BadRequestError):
        log.info("bad_request", detail=exc.detail, path=str(request.url))
        return JSONResponse(status_code=400, content={"detail": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError):
        payload = _validation_payload(exc)
        log.info("request_validation_error", path=str(request.url), errors=payload.get("errors", []))
        return JSONResponse(status_code=422, content=payload)

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(request: Request, exc: ValidationError):
        payload = _validation_payload(exc)
        log.info("pydantic_validation_error", path=str(request.url), errors=payload.get("errors", []))
        return JSONResponse(status_code=422, content=payload)

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception):
        log.exception("unhandled_exception", path=str(request.url))
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
