"""Public error envelope and the exception handlers that produce it."""

import logging
import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from vehicle_price.domain import BusyError, ContractError

logger = logging.getLogger(__name__)


def error_response(
    request: Request, status: int, code: str, message: str, headers=None
) -> JSONResponse:
    """Build the service's consistent public error response."""
    request_id = getattr(request.state, "request_id", None)
    response_headers = dict(headers or {})
    if request_id is not None:
        response_headers["X-Request-ID"] = request_id
    return JSONResponse(
        status_code=status,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": request_id,
            }
        },
        headers=response_headers,
    )


def log_rejection(request: Request, log_message: str, event: str, code: str) -> None:
    """Log a client-facing rejection with its correlation ID and error code."""
    logger.warning(
        log_message,
        extra={
            "event": event,
            "request_id": request.state.request_id,
            "outcome": "failure",
            "error_code": code,
        },
    )


def register_error_handlers(app: FastAPI) -> None:
    """Map domain and framework exceptions to the public error envelope."""

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        """Map request schema failures to the public validation error."""
        log_rejection(
            request, "Request validation failed", "request_rejected", "invalid_request"
        )
        return error_response(
            request, 422, "invalid_request", "Request schema validation failed"
        )

    @app.exception_handler(ContractError)
    async def contract_error(request: Request, exc: ContractError):
        """Map model contract failures to an invalid-feature response."""
        log_rejection(
            request, "Model feature rejected", "request_rejected", "invalid_feature"
        )
        return error_response(request, 422, "invalid_feature", str(exc))

    @app.exception_handler(BusyError)
    async def busy_error(request: Request, exc: BusyError):
        """Map exhausted inference capacity to a retryable response."""
        log_rejection(
            request,
            "Inference capacity exhausted",
            "prediction_rejected",
            "capacity_exhausted",
        )
        return error_response(
            request, 503, "capacity_exhausted", str(exc), {"Retry-After": "1"}
        )

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        """Log unexpected failures while hiding internal details from clients."""
        logger.error(
            "Prediction failed",
            extra={
                "event": "prediction_failed",
                "request_id": getattr(request.state, "request_id", None),
                "outcome": "failure",
                "duration_ms": round(
                    (time.perf_counter() - request.state.inference_started) * 1000, 3
                )
                if hasattr(request.state, "inference_started")
                else None,
                "model_version": getattr(request.state, "model_version", None),
                "error_code": "internal_error",
            },
            exc_info=(type(exc), exc, exc.__traceback__),
        )
        return error_response(request, 500, "internal_error", "Prediction failed")
