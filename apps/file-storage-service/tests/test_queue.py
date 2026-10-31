import base64
import json
from unittest.mock import AsyncMock

import pytest

from app.queue import MESSAGE_SCHEMA, StorageConsumer


@pytest.mark.asyncio
async def test_consumer_writes_payload_before_ack(tmp_path):
    message = AsyncMock()
    message.body = json.dumps(
        {
            "schema": MESSAGE_SCHEMA,
            "job_id": "job-1",
            "filename": "readers.csv",
            "content_base64": base64.b64encode(b"id,name\n").decode("ascii"),
        }
    ).encode()
    consumer = StorageConsumer("amqp://unused", tmp_path)

    await consumer._handle(message)

    assert (tmp_path / "readers.csv").read_bytes() == b"id,name\n"
    message.ack.assert_awaited_once()
    message.reject.assert_not_awaited()


@pytest.mark.asyncio
async def test_consumer_rejects_unsafe_filename(tmp_path):
    message = AsyncMock()
    message.body = json.dumps(
        {
            "schema": MESSAGE_SCHEMA,
            "job_id": "job-1",
            "filename": "../readers.csv",
            "content_base64": base64.b64encode(b"bad").decode("ascii"),
        }
    ).encode()
    consumer = StorageConsumer("amqp://unused", tmp_path)

    await consumer._handle(message)

    message.reject.assert_awaited_once_with(requeue=False)
    assert not list(tmp_path.iterdir())


@pytest.mark.asyncio
async def test_consumer_rejects_directory_filename(tmp_path):
    message = AsyncMock()
    message.body = json.dumps(
        {
            "schema": MESSAGE_SCHEMA,
            "job_id": "job-1",
            "filename": ".",
            "content_base64": base64.b64encode(b"bad").decode("ascii"),
        }
    ).encode()
    consumer = StorageConsumer("amqp://unused", tmp_path)

    await consumer._handle(message)

    message.reject.assert_awaited_once_with(requeue=False)
