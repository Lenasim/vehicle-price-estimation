"""Export the FastAPI-generated OpenAPI contract for review and tooling."""

import json
from pathlib import Path

from vehicle_price.main import app

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "openapi.json"


def main() -> None:
    """Write a deterministic snapshot generated from the application source."""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n")
    print(f"OpenAPI contract written to {OUTPUT}")


if __name__ == "__main__":
    main()
