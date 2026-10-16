# Technical Test — Vehicle Price Estimation API

**Role:** Senior ML Engineer
**Estimated effort:** 3–5 hours (take-home, no hard deadline pressure — we care about how you work, not how fast)

## Context

We estimate the market value ("cote") of used vehicles from a few basic attributes. Data
science has already trained and shipped a model; your job is to bring it into production
behind a clean, well-engineered inference API.

## What you're given

- `price estimation model- training.ipynb` — the training notebook, for context on how the
  model was built. You do not need to run or modify it.
- `artifacts/model_pipeline.joblib` — a fitted `scikit-learn` `Pipeline` (feature
  preprocessing + XGBoost regressor) that exposes a standard `.predict(dataframe)` interface.
- `artifacts/metadata.json` — the feature contract: allowed values for categorical fields,
  expected types, model version, and the metrics measured on the held-out test set.

You are **not** expected to touch model training or feature engineering. Treat the
`.joblib` file as a black box you load and call.

## Your task

Build a Python inference API that serves price predictions from this model.

**Request** (conceptually — design the exact schema yourself):
- `marque`: one of the values in `metadata.json["features"]["marque"]["allowed_values"]`
- `date_first_circulation`: date, `YYYY-MM-DD`
- `km`: non-negative number
- `gearbox`: one of the values in `metadata.json["features"]["gearbox"]["allowed_values"]`

**Response:** the predicted price, plus enough metadata (e.g. model version) for a caller
to know what produced the number.

Use whichever framework you're most comfortable with (FastAPI, Flask, or another one) —
we're evaluating engineering judgment, not framework choice.

## Requirements

**Functional**
- A prediction endpoint that loads the provided pipeline. Please pay attention to performance optimization. Identify and implement appropriate optimizations to improve application performance and resource utilization. Avoid redundancy. 
- Sensible HTTP status codes and error bodies.
- A health/liveness endpoint suitable for a load balancer or orchestrator.


**Engineering Quality**
- Ensure the code is clean, maintainable, robust, and follows good engineering practices.
- Apply appropriate practices to ensure the application is reliable, testable, and easy to run.
- Document the project appropriately.

## Deliverables

A git repository (zip export or a link) It should run end-to-end from your instructions. 

## Evaluation criteria

* API design & correctness 
* Code quality 
* Docs & deliverable completeness 
* Engineering quality
* Prod ready code

## Any questions?

We're happy to answer clarifying questions — treat ambiguity the way you would on a real
team: make a reasonable call, and note it in your README.
