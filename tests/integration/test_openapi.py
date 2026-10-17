import json
from pathlib import Path

from vehicle_price.main import app

ROOT = Path(__file__).resolve().parents[2]


def test_documentation_endpoints_are_available(client):
    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_openapi_documents_public_contract():
    schema = app.openapi()
    predict = schema["paths"]["/predict"]["post"]
    health = schema["paths"]["/health"]["get"]

    assert predict["summary"] == "Estimate one vehicle price"
    assert set(predict["responses"]) == {"200", "422", "500", "503"}
    assert predict["responses"]["422"]["content"]["application/json"]["examples"]
    assert "Retry-After" in predict["responses"]["503"]["headers"]
    assert health["summary"] == "Check model readiness"
    assert set(health["responses"]) == {"200", "503"}


def test_exported_openapi_is_in_sync():
    exported = json.loads((ROOT / "docs" / "openapi.json").read_text())
    assert exported == app.openapi()
