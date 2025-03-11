from hypurrquant_fastapi_core.logging_config import configure_logging
from hypurrquant_fastapi_core.singleton import singleton

import asyncio
import json
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from abc import ABC, abstractmethod
import aioboto3
from typing import Any

logger = configure_logging(__name__)


class AsyncMessagingProducer(ABC):

    @abstractmethod
    async def start(self):
        """클라이언트를 초기화합니다."""
        pass

    @abstractmethod
    async def stop(self):
        """클라이언트를 종료합니다."""
        pass

    @abstractmethod
    async def send_message(self, destination, message: Any):
        """
        destination: Kafka에서는 topic, SQS에서는 큐 URL 등 (구현체에 따라 사용)
        message: 전송할 데이터 (dict)
        """


@singleton
class KafkaMessagingProducer(AsyncMessagingProducer):
    def __init__(
        self,
        bootstrap_servers: str,
        loop=None,
    ):
        self.loop = loop or asyncio.get_event_loop()
        self.bootstrap_servers = bootstrap_servers
        self.producer = AIOKafkaProducer(
            loop=self.loop,
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    async def start(self):
        await self.producer.start()

    async def stop(self):
        await self.producer.stop()

    async def send_message(self, destination: str, message: Any):
        # destination은 여기서는 topic과 동일하게 사용됩니다.
        await self.producer.send(destination, message)
        await self.producer.flush()


@singleton
class SQSMessagingProducer(AsyncMessagingProducer):
    def __init__(self, region_name: str):
        self.region_name = region_name
        self.session = aioboto3.Session()
        self.client = None

    async def start(self):
        self.client = await self.session.client(
            "sqs", region_name=self.region_name
        ).__aenter__()

    async def stop(self):
        if self.client:
            await self.client.__aexit__(None, None, None)

    async def send_message(self, destination: str, message: Any):
        await self.client.send_message(
            QueueUrl=destination, MessageBody=json.dumps(message)
        )


class AsyncMessagingConsumer(ABC):

    @abstractmethod
    async def start(self):
        """클라이언트를 초기화합니다."""
        pass

    @abstractmethod
    async def stop(self):
        """클라이언트를 종료합니다."""
        pass

    @abstractmethod
    async def consume_messages(self):
        """
        destination: Kafka에서는 topic, SQS에서는 큐 URL 등 (구현체에 따라 사용)
        async generator 형태로 메시지를 yield합니다.
        """
        pass


class KafkaMessagingConsumer(AsyncMessagingConsumer):
    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        group_id: str = "default-group",
        loop=None,
    ):
        self.topic = topic
        self.loop = loop or asyncio.get_event_loop()
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            auto_offset_reset="earliest",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )

    async def start(self):
        await self.consumer.start()

    async def stop(self):
        await self.consumer.stop()

    async def consume_messages(self):
        # destination은 topic; 여기서 Kafka Consumer가 계속 yield하도록 함.
        try:
            async for msg in self.consumer:
                yield msg.value
        except Exception as e:
            print("Kafka Consumer 에러:", e)


class SQSMessagingConsumer(AsyncMessagingConsumer):
    def __init__(self, queue_url: str, region_name: str):
        self.queue_url = queue_url
        self.region_name = region_name
        self.session = aioboto3.Session()
        self.client = None

    async def start(self):
        self.client = await self.session.client(
            "sqs", region_name=self.region_name
        ).__aenter__()

    async def stop(self):
        if self.client:
            await self.client.__aexit__(None, None, None)

    async def consume_messages(self):
        # SQS는 폴링 방식을 사용합니다.
        while True:
            response = await self.client.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20,  # long polling
            )
            messages = response.get("Messages", [])
            for m in messages:
                yield json.loads(m["Body"])
                # 메시지 처리 후 삭제
                await self.client.delete_message(
                    QueueUrl=self.queue_url, ReceiptHandle=m["ReceiptHandle"]
                )
            # 짧은 대기 후 다시 폴링
            await asyncio.sleep(0.1)
