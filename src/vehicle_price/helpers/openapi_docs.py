"""OpenAPI metadata and response documentation for the public routes."""

from vehicle_price.domain import ErrorResponse

OPENAPI_TAGS = [
    {
        "name": "Inference",
        "description": "Validate one vehicle and return a versioned price estimate.",
    },
    {
        "name": "Operations",
        "description": "Inspect local worker readiness.",
    },
]

HEALTH_RESPONSES = {
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
}

PREDICT_RESPONSES = {
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
}
