FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src/ src/
RUN uv sync --frozen --no-dev

COPY artifacts/ artifacts/

RUN useradd --system --uid 10001 app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=15s \
    CMD ["/app/.venv/bin/python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]

CMD ["/app/.venv/bin/gunicorn", "vehicle_price.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "2", \
     "--bind", "0.0.0.0:8000"]