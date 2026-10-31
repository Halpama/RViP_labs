import base64
import json
from unittest.mock import AsyncMock

import pytest

from app.queue import MESSAGE_SCHEMA, ReportPublisher


@pytest.mark.asyncio
async def test_publisher_sends_persistent_export_message():
    exchange = AsyncMock()
    publisher = ReportPublisher("amqp://unused")
    publisher.exchange = exchange

    job_id = await publisher.publish("readers.csv", b"id,name\n")

    message = exchange.publish.await_args.args[0]
    payload = json.loads(message.body)
    assert payload == {
        "schema": MESSAGE_SCHEMA,
        "job_id": str(job_id),
        "filename": "readers.csv",
        "content_base64": base64.b64encode(b"id,name\n").decode("ascii"),
    }
    assert message.delivery_mode.name == "PERSISTENT"
