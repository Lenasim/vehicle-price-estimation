import logging
import time
from contextlib import asynccontextmanager
from uuid import uuid4

import anyio
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from vehicle_price.adapters import JoblibPredictor
from vehicle_price.domain import (
    BusyError,
    ContractError,
    ErrorResponse,
    HealthResponse,
    Prediction,
    Vehicle,
)
from vehicle_price.infrastructure import load_metadata, load_pipeline
from vehicle_price.observability import configure_application_logging
from vehicle_price.service import PredictionService
from vehicle_price.settings import Settings

configure_application_logging()
logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI application and wire its dependencies."""
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Load model resources once per worker and release app state on shutdown."""
        logger.info(
            "Loading model",
            extra={
                "event": "model_loading",
                "model_path": str(settings.model_pipeline_path),
            },
        )
        metadata = load_metadata(settings.metadata_path)
        pipeline = load_pipeline(settings.model_pipeline_path)
        # Bound the sync endpoint thread pool as well as actual model concurrency.
        anyio.to_thread.current_default_thread_limiter().total_tokens = (
            settings.inference_concurrency + 4
        )
        app.state.service = PredictionService(
            JoblibPredictor(pipeline), metadata, settings.inference_concurrency
        )
        logger.info(
            "Model ready",
            extra={
                "event": "model_ready",
                "model_version": metadata.model_version,
            },
        )
        try:
            yield
        finally:
            app.state.service = None

    app = FastAPI(
        title="Vehicle Price Estimation API",
        description=(
            "Serve one vehicle price estimate from the supplied model pipeline. "
            "The model is loaded once per worker and every prediction identifies "
            "the model version that produced it."
        ),
        version="1.0.0",
        lifespan=lifespan,
        openapi_tags=[
            {
                "name": "Inference",
                "description": "Validate one vehicle and return a versioned price estimate.",
            },
            {
                "name": "Operations",
                "description": "Inspect local worker readiness.",
            },
        ],
    )

    def log_request(request: Request, status_code: int, started: float) -> None:
        """Log the completed request with its correlation ID and duration."""
        logger.info(
            "Request completed",
            extra={
                "event": "request_completed",
                "request_id": request.state.request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "outcome": "success" if status_code < 400 else "failure",
                "duration_ms": round((time.perf_counter() - started) * 1000, 3),
            },
        )

    @app.middleware("http")
    async def request_log(request: Request, call_next):
        """Attach a request ID and log request duration and status."""
        request.state.request_id = str(uuid4())
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            log_request(request, 500, started)
            raise
        response.headers["X-Request-ID"] = request.state.request_id
        log_request(request, response.status_code, started)
        return response

    def error(request: Request, status: int, code: str, message: str, headers=None):
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

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        """Map request schema failures to the public validation error."""
        logger.warning(
            "Request validation failed",
            extra={
                "event": "request_rejected",
                "request_id": request.state.request_id,
                "outcome": "failure",
                "error_code": "invalid_request",
            },
        )
        return error(
            request, 422, "invalid_request", "Request schema validation failed"
        )

    @app.exception_handler(ContractError)
    async def contract_error(request: Request, exc: ContractError):
        """Map model contract failures to an invalid-feature response."""
        logger.warning(
            "Model feature rejected",
            extra={
                "event": "request_rejected",
                "request_id": request.state.request_id,
                "outcome": "failure",
                "error_code": "invalid_feature",
            },
        )
        return error(request, 422, "invalid_feature", str(exc))

    @app.exception_handler(BusyError)
    async def busy_error(request: Request, exc: BusyError):
        """Map exhausted inference capacity to a retryable response."""
        logger.warning(
            "Inference capacity exhausted",
            extra={
                "event": "prediction_rejected",
                "request_id": request.state.request_id,
                "outcome": "failure",
                "error_code": "capacity_exhausted",
            },
        )
        return error(request, 503, "capacity_exhausted", str(exc), {"Retry-After": "1"})

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
        return error(request, 500, "internal_error", "Prediction failed")

    @app.get(
        "/health",
        response_model=HealthResponse,
        tags=["Operations"],
        summary="Check model readiness",
        description=(
            "Return 200 only when this worker has loaded the model and metadata. "
            "This is a readiness check, not an end-to-end prediction."
        ),
        responses={
            503: {
                "model": ErrorResponse,
                "description": "The model is not available in this worker.",
                "content": {
                    "application/json": {
                        "example": {
                            "error": {
                                "code": "not_ready",
                                "message": "Model is unavailable",
                                "request_id": "5a5e38e2-b76f-41ad-9954-4a9f874a7f50",
                            }
                        }
                    }
                },
            }
        },
    )
    async def health(request: Request) -> HealthResponse | JSONResponse:
        """Report whether this worker has a ready prediction service."""
        service = getattr(request.app.state, "service", None)
        if service is None:
            return error(request, 503, "not_ready", "Model is unavailable")
        return HealthResponse(model_version=service.metadata.model_version)

    @app.post(
        "/predict",
        response_model=Prediction,
        tags=["Inference"],
        summary="Estimate one vehicle price",
        description=(
            "Validate the four model features, invoke the preloaded pipeline, and "
            "return its finite non-negative output without display rounding. "
            "Allowed brands and gearboxes come from the loaded metadata."
        ),
        responses={
            422: {
                "model": ErrorResponse,
                "description": "The request schema or model feature contract is invalid.",
                "content": {
                    "application/json": {
                        "examples": {
                            "schema_error": {
                                "summary": "Missing or malformed field",
                                "value": {
                                    "error": {
                                        "code": "invalid_request",
                                        "message": "Request schema validation failed",
                                        "request_id": "5a5e38e2-b76f-41ad-9954-4a9f874a7f50",
                                    }
                                },
                            },
                            "unsupported_category": {
                                "summary": "Value rejected by model metadata",
                                "value": {
                                    "error": {
                                        "code": "invalid_feature",
                                        "message": "Unsupported marque: peugeot",
                                        "request_id": "5a5e38e2-b76f-41ad-9954-4a9f874a7f50",
                                    }
                                },
                            },
                        }
                    }
                },
            },
            500: {
                "model": ErrorResponse,
                "description": "Prediction failed after validation.",
            },
            503: {
                "model": ErrorResponse,
                "description": "Inference capacity is temporarily exhausted.",
                "headers": {
                    "Retry-After": {
                        "description": "Seconds before the caller should retry.",
                        "schema": {"type": "integer", "example": 1},
                    }
                },
            },
        },
    )
    def predict(vehicle: Vehicle, request: Request):
        """Return a price prediction for one validated vehicle."""
        service = request.app.state.service
        request.state.inference_started = time.perf_counter()
        request.state.model_version = service.metadata.model_version
        prediction = service.predict(vehicle)
        logger.info(
            "Prediction completed",
            extra={
                "event": "prediction_completed",
                "request_id": request.state.request_id,
                "outcome": "success",
                "duration_ms": round(
                    (time.perf_counter() - request.state.inference_started) * 1000, 3
                ),
                "model_version": prediction.model_version,
                "predicted_price": prediction.predicted_price,
            },
        )
        return prediction

    return app


app = create_app()
