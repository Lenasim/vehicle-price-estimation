.PHONY: install dev health predict test lint openapi smoke-model smoke-zip docker-build docker-run

API_URL ?= http://localhost:8000

install:
	uv sync --all-groups

dev:
	uv run uvicorn vehicle_price.main:app --reload --host 0.0.0.0 --port 8000

health:
	curl --fail --silent --show-error --write-out '\n' $(API_URL)/health

predict:
	curl --fail --silent --show-error --write-out '\n' \
		--header 'Content-Type: application/json' \
		--data '{"marque":"bmw","date_first_circulation":"2018-03-01","km":108946,"gearbox":"auto"}' \
		$(API_URL)/predict

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check .
	uv run ruff format --check .

openapi:
	uv run python scripts/export_openapi.py

smoke-model:
	uv run python -m scripts.smoke_model

smoke-zip:
	uv run python scripts/smoke_zip.py

docker-build:
	docker build -t vehicle-price-api:latest .

docker-run:
	docker run --rm -p 8000:8000 vehicle-price-api:latest
