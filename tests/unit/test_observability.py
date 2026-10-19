import json
import logging
import sys

from vehicle_price.helpers.observability import JsonFormatter


def test_json_formatter_emits_structured_fields_and_exception():
    try:
        raise RuntimeError("prediction failed")
    except RuntimeError:
        record = logging.getLogger("vehicle_price.test").makeRecord(
            name="vehicle_price.test",
            level=logging.ERROR,
            fn=__file__,
            lno=1,
            msg="Prediction failed",
            args=(),
            exc_info=sys.exc_info(),
            extra={
                "event": "prediction_failed",
                "request_id": "request-123",
                "outcome": "failure",
                "error_code": "internal_error",
            },
        )

    payload = json.loads(JsonFormatter().format(record))

    assert payload["event"] == "prediction_failed"
    assert payload["request_id"] == "request-123"
    assert payload["outcome"] == "failure"
    assert payload["error_code"] == "internal_error"
    assert "RuntimeError: prediction failed" in payload["exception"]
