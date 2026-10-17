import logging

import pytest
from fastapi.testclient import TestClient

from vehicle_price.main import create_app


class RecordCollector(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


@pytest.fixture(scope="session")
def client():
    app = create_app()
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def application_logs():
    collector = RecordCollector()
    logger = logging.getLogger("vehicle_price")
    logger.addHandler(collector)
    try:
        yield collector.records
    finally:
        logger.removeHandler(collector)
