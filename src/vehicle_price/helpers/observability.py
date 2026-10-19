"""Structured application logging without external runtime dependencies."""

import json
import logging
from datetime import UTC, datetime

APPLICATION_LOGGER = "vehicle_price"
STRUCTURED_FIELDS = (
    "event",
    "request_id",
    "method",
    "path",
    "status_code",
    "outcome",
    "duration_ms",
    "model_version",
    "predicted_price",
    "error_code",
    "model_path",
)


class JsonFormatter(logging.Formatter):
    """Serialize application log records as one JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in STRUCTURED_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)


def configure_application_logging() -> logging.Logger:
    """Configure the package logger once and return it."""
    application_logger = logging.getLogger(APPLICATION_LOGGER)
    if not application_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        application_logger.addHandler(handler)
    application_logger.setLevel(logging.INFO)
    application_logger.propagate = False
    return application_logger
