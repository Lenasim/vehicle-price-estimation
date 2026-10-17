"""Quick end-to-end smoke test for the saved model artifact."""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.model_loader import load_pipeline  # noqa: E402

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
