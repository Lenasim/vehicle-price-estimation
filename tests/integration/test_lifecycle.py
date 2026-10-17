import importlib

import pytest
from fastapi.testclient import TestClient

from vehicle_price.main import create_app
from vehicle_price.settings import Settings

main_module = importlib.import_module("vehicle_price.main")


def test_model_resources_load_once_per_app_lifespan(monkeypatch):
    calls = {"metadata": 0, "pipeline": 0}
    real_load_metadata = main_module.load_metadata
    real_load_pipeline = main_module.load_pipeline

    def counted_load_metadata(path):
        calls["metadata"] += 1
        return real_load_metadata(path)

    def counted_load_pipeline(path):
        calls["pipeline"] += 1
        return real_load_pipeline(path)

    monkeypatch.setattr(main_module, "load_metadata", counted_load_metadata)
    monkeypatch.setattr(main_module, "load_pipeline", counted_load_pipeline)

    with TestClient(create_app()) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/health").status_code == 200

    assert calls == {"metadata": 1, "pipeline": 1}


def test_startup_fails_when_model_is_missing(tmp_path):
    settings = Settings(model_pipeline_path=tmp_path / "missing.joblib")

    with pytest.raises(FileNotFoundError), TestClient(create_app(settings)):
        pass
