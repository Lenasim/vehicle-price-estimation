import pytest

VALID_PAYLOAD = {
    "marque": "bmw",
    "date_first_circulation": "2018-03-01",
    "km": 108946,
    "gearbox": "auto",
}


class FailingPredictor:
    def predict(self, vehicle):
        raise RuntimeError("prediction failed")


def test_predict_success(client):
    response = client.post("/predict", json=VALID_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_price"] > 0
    assert data["model_version"] == "1.0.0"
    assert "currency" not in data


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.parametrize(
    ("payload", "error_code"),
    [
        ({**VALID_PAYLOAD, "marque": "peugeot"}, "invalid_feature"),
        ({**VALID_PAYLOAD, "gearbox": "cvt"}, "invalid_feature"),
        (
            {k: v for k, v in VALID_PAYLOAD.items() if k != "date_first_circulation"},
            "invalid_request",
        ),
        ({**VALID_PAYLOAD, "km": -500}, "invalid_request"),
        ({**VALID_PAYLOAD, "km": "108946"}, "invalid_request"),
        (
            {**VALID_PAYLOAD, "date_first_circulation": "2099-01-01", "km": 0},
            "invalid_request",
        ),
        (
            {**VALID_PAYLOAD, "owner_name": "must not be accepted or logged"},
            "invalid_request",
        ),
    ],
    ids=[
        "unknown_brand",
        "unknown_gearbox",
        "missing_field",
        "negative_km",
        "string_km",
        "future_date",
        "unknown_field",
    ],
)
def test_invalid_payload_returns_422(client, payload, error_code):
    response = client.post("/predict", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == error_code


def test_prediction_failure_returns_traceable_500(
    client, monkeypatch, application_logs
):
    monkeypatch.setattr(client.app.state.service, "predictor", FailingPredictor())

    response = client.post("/predict", json=VALID_PAYLOAD)

    assert response.status_code == 500
    assert response.json()["error"]["request_id"] == response.headers["X-Request-ID"]
    failure = next(
        record for record in application_logs if record.event == "prediction_failed"
    )
    assert failure.request_id == response.headers["X-Request-ID"]
    assert failure.model_version == "1.0.0"
    assert failure.error_code == "internal_error"


def test_success_and_error_responses_include_request_id(client):
    success = client.get("/health")
    failure = client.post("/predict", json={})

    assert success.headers["X-Request-ID"]
    assert failure.headers["X-Request-ID"]
    assert failure.json()["error"]["request_id"] == failure.headers["X-Request-ID"]


class UnavailableSlots:
    def acquire(self, blocking):
        return False


def test_capacity_exhaustion_returns_retryable_503(client, monkeypatch):
    monkeypatch.setattr(client.app.state.service, "slots", UnavailableSlots())

    response = client.post("/predict", json=VALID_PAYLOAD)

    assert response.status_code == 503
    assert response.headers["Retry-After"] == "1"
    assert response.json()["error"]["code"] == "capacity_exhausted"


def test_health_returns_503_without_ready_service(client):
    service = client.app.state.service
    client.app.state.service = None
    try:
        response = client.get("/health")
    finally:
        client.app.state.service = service

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "not_ready"


def test_successful_prediction_emits_structured_business_log(client, application_logs):
    response = client.post("/predict", json=VALID_PAYLOAD)

    prediction_log = next(
        record for record in application_logs if record.event == "prediction_completed"
    )
    assert prediction_log.request_id == response.headers["X-Request-ID"]
    assert prediction_log.outcome == "success"
    assert prediction_log.model_version == response.json()["model_version"]
    assert prediction_log.predicted_price == response.json()["predicted_price"]
    assert prediction_log.duration_ms >= 0
    assert not hasattr(prediction_log, "vehicle")
