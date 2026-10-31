import base64
import json
from uuid import UUID, uuid4

import aio_pika
from aio_pika import DeliveryMode, ExchangeType, Message
from aio_pika.exceptions import AMQPException


EXPORT_EXCHANGE = "library.reports"
EXPORT_QUEUE = "library.file-storage"
EXPORT_ROUTING_KEY = "report.export"
MESSAGE_SCHEMA = "report-export.v1"


class ReportPublisher:
    def __init__(self, amqp_url: str) -> None:
        self.amqp_url = amqp_url
        self.connection: aio_pika.abc.AbstractRobustConnection | None = None
        self.channel: aio_pika.abc.AbstractRobustChannel | None = None
        self.exchange: aio_pika.abc.AbstractExchange | None = None

    async def connect(self) -> None:
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel(publisher_confirms=True)
        self.exchange = await self.channel.declare_exchange(
            EXPORT_EXCHANGE,
            ExchangeType.DIRECT,
            durable=True,
        )
        queue = await self.channel.declare_queue(EXPORT_QUEUE, durable=True)
        await queue.bind(self.exchange, routing_key=EXPORT_ROUTING_KEY)

    async def close(self) -> None:
        if self.connection is not None:
            await self.connection.close()

    async def publish(self, filename: str, content: bytes) -> UUID:
        if self.exchange is None:
            raise RuntimeError("report publisher is not connected")

        job_id = uuid4()
        payload = {
            "schema": MESSAGE_SCHEMA,
            "job_id": str(job_id),
            "filename": filename,
            "content_base64": base64.b64encode(content).decode("ascii"),
        }
        await self.exchange.publish(
            Message(
                json.dumps(payload).encode("utf-8"),
                content_type="application/json",
                delivery_mode=DeliveryMode.PERSISTENT,
                message_id=str(job_id),
            ),
            routing_key=EXPORT_ROUTING_KEY,
        )
        return job_id
