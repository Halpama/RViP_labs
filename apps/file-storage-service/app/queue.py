import asyncio
import base64
import binascii
import json
import logging
import re
from pathlib import Path

import aio_pika
from aio_pika import ExchangeType

EXPORT_EXCHANGE = "library.reports"
EXPORT_QUEUE = "library.file-storage"
EXPORT_ROUTING_KEY = "report.export"
MESSAGE_SCHEMA = "report-export.v1"
SAFE_FILENAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
RECONNECT_DELAY = 5
queue_logger = logging.getLogger("queue")


class StorageConsumer:
    def __init__(self, amqp_url: str, storage_root: Path) -> None:
        self.amqp_url = amqp_url
        self.storage_root = storage_root
        self.connection: aio_pika.abc.AbstractRobustConnection | None = None
        self.channel: aio_pika.abc.AbstractRobustChannel | None = None
        self.task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        self.task = asyncio.create_task(self._run())

    async def close(self) -> None:
        if self.task is not None:
            self.task.cancel()
            await asyncio.gather(self.task, return_exceptions=True)
        if self.connection is not None:
            await self.connection.close()

    async def _run(self) -> None:
        while True:
            try:
                self.connection = await aio_pika.connect_robust(self.amqp_url)
                self.channel = await self.connection.channel()
                exchange = await self.channel.declare_exchange(
                    EXPORT_EXCHANGE,
                    ExchangeType.DIRECT,
                    durable=True,
                )
                queue = await self.channel.declare_queue(EXPORT_QUEUE, durable=True)
                await queue.bind(exchange, routing_key=EXPORT_ROUTING_KEY)
                await self._consume(queue)
            except asyncio.CancelledError:
                raise
            except (aio_pika.AMQPException, OSError) as error:
                queue_logger.warning(
                    "RabbitMQ connection failed; retrying in %s seconds: %s",
                    RECONNECT_DELAY,
                    error,
                )
                await asyncio.sleep(RECONNECT_DELAY)
            finally:
                if self.connection is not None:
                    await self.connection.close()
                    self.connection = None
                    self.channel = None

    async def _consume(self, queue: aio_pika.abc.AbstractQueue) -> None:
        async with queue.iterator() as messages:
            async for message in messages:
                await self._handle(message)

    async def _handle(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        try:
            payload = json.loads(message.body)
            filename = payload["filename"]
            content = base64.b64decode(payload["content_base64"], validate=True)
            if payload["schema"] != MESSAGE_SCHEMA or not isinstance(filename, str):
                raise ValueError("invalid report export message")
            if not SAFE_FILENAME.fullmatch(filename):
                raise ValueError("invalid report filename")
        except (KeyError, TypeError, ValueError, UnicodeDecodeError, binascii.Error):
            await message.reject(requeue=False)
            return

        self.storage_root.mkdir(parents=True, exist_ok=True)
        destination = (self.storage_root / filename).resolve()
        if destination.parent != self.storage_root.resolve():
            await message.reject(requeue=False)
            return
        try:
            destination.write_bytes(content)
        except OSError:
            await message.nack(requeue=True)
            return
        await message.ack()
