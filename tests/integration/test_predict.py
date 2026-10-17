class FailingPredictor:
    def predict(self, vehicle):
        raise RuntimeError("prediction failed")


def test_predict_success(client):
    response = client.post(
        "/predict",
        json={
            "marque": "bmw",
            "date_first_circulation": "2018-03-01",
            "km": 108946,
            "gearbox": "auto",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_price"] > 0
    assert data["model_version"] == "1.0.0"
    assert "currency" not in data


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_unknown_brand_returns_422(client):
    response = client.post(
        "/predict",
        json={
            "marque": "peugeot",
            "date_first_circulation": "2018-03-01",
            "km": 108946,
            "gearbox": "auto",
        },
    )
    assert response.status_code == 422


def test_missing_field_returns_422(client):
    response = client.post(
        "/predict",
        json={
            "marque": "bmw",
            "km": 108946,
            "gearbox": "auto",
        },
    )
    assert response.status_code == 422


def test_negative_km_returns_422(client):
    response = client.post(
        "/predict",
        json={
            "marque": "bmw",
            "date_first_circulation": "2018-03-01",
            "km": -500,
            "gearbox": "auto",
        },
    )
    assert response.status_code == 422


def test_future_registration_date_returns_422(client):
    response = client.post(
        "/predict",
        json={
            "marque": "bmw",
            "date_first_circulation": "2099-01-01",
            "km": 0,
            "gearbox": "auto",
        },
    )
    assert response.status_code == 422


def test_prediction_failure_returns_traceable_500(
    client, monkeypatch, application_logs
):
    monkeypatch.setattr(client.app.state.service, "predictor", FailingPredictor())

    response = client.post(
        "/predict",
        json={
            "marque": "bmw",
            "date_first_circulation": "2018-03-01",
            "km": 108946,
            "gearbox": "auto",
        },
    )

    assert response.status_code == 500
    assert response.json()["error"]["request_id"] == response.headers["X-Request-ID"]
    failure = next(
        record for record in application_logs if record.event == "prediction_failed"
    )
    assert failure.request_id == response.headers["X-Request-ID"]
    assert failure.model_version == "1.0.0"
    assert failure.error_code == "internal_error"


def test_unknown_field_returns_422(client):
    response = client.post(
        "/predict",
        json={
            "marque": "bmw",
            "date_first_circulation": "2018-03-01",
            "km": 108946,
            "gearbox": "auto",
            "owner_name": "must not be accepted or logged",
        },
    )
    assert response.status_code == 422


def test_string_mileage_returns_422(client):
    response = client.post(
        "/predict",
        json={
            "marque": "bmw",
            "date_first_circulation": "2018-03-01",
            "km": "108946",
            "gearbox": "auto",
        },
    )
    assert response.status_code == 422


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

    response = client.post(
        "/predict",
        json={
            "marque": "bmw",
            "date_first_circulation": "2018-03-01",
            "km": 108946,
            "gearbox": "auto",
        },
    )

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
    response = client.post(
        "/predict",
        json={
            "marque": "bmw",
            "date_first_circulation": "2018-03-01",
            "km": 108946,
            "gearbox": "auto",
        },
    )

    prediction_log = next(
        record for record in application_logs if record.event == "prediction_completed"
    )
    assert prediction_log.request_id == response.headers["X-Request-ID"]
    assert prediction_log.outcome == "success"
    assert prediction_log.model_version == response.json()["model_version"]
    assert prediction_log.predicted_price == response.json()["predicted_price"]
    assert prediction_log.duration_ms >= 0
    assert not hasattr(prediction_log, "vehicle")
