import logging
import structlog
from .config import settings
from __future__ import annotations
from structlog.processors import TimeStamper
from app.core.context import request_id  # <-- import the context var


structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(),  # pretty in dev; JSON later in prod
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
)

def add_request_id(_, __, event_dict):
    rid = request_id.get()
    if rid:
        event_dict["request_id"] = rid
    return event_dict

def setup_logging(level: str = "INFO") -> None:
    structlog.configure(
        processors=[
            TimeStamper(fmt="iso"),                # timestamp
            structlog.processors.add_log_level,    # level
            add_request_id,                        # <-- add request_id
            structlog.processors.EventRenamer("message"),
            structlog.processors.JSONRenderer(),   # nice structured JSON
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(structlog, level, 20)),
        cache_logger_on_first_use=True,
    )