"""Quick end-to-end smoke test for the saved model artifact."""

import json
from pathlib import Path

import pandas as pd

from vehicle_price.infrastructure import load_pipeline

ARTIFACTS = Path(__file__).parent.parent / "artifacts"

pipeline = load_pipeline(ARTIFACTS / "model_pipeline.joblib")
metadata = json.loads((ARTIFACTS / "metadata.json").read_text())

print(f"model_version={metadata['model_version']}")

sample = pd.DataFrame(
    [
        {
            "marque": "bmw",
            "date_first_circulation": "2018-03-01",
            "km": 108946,
            "gearbox": "auto",
        }
    ]
)

prediction = pipeline.predict(sample)[0]
print(f"prediction={prediction}")
