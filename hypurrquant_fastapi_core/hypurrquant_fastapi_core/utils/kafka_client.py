import json
import logging
import asyncio
from typing import Any, Callable, Optional
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class AioKafkaProducerClient:
    def __init__(self, bootstrap_servers: str, loop: asyncio.AbstractEventLoop):
        """
        aiokafka 프로듀서 초기화

        :param bootstrap_servers: Kafka 브로커 주소 (예: "localhost:9092")
        :param loop: asyncio 이벤트 루프
        """
        self.bootstrap_servers = bootstrap_servers
        self.loop = loop
        self.producer: Optional[AIOKafkaProducer] = None

    async def start(self) -> None:
        """
        프로듀서를 시작합니다.
        """
        self.producer = AIOKafkaProducer(
            loop=self.loop,
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self.producer.start()
        logger.debug("aiokafka Producer started.")

    async def send_message(self, topic: str, message: Any) -> None:
        """
        지정한 토픽에 메시지를 전송합니다.
        """
        if self.producer is None:
            raise RuntimeError("Producer has not been started. Call start() first.")
        # send_and_wait: 메시지가 전송될 때까지 기다림.
        await self.producer.send_and_wait(topic, message)
        logger.debug(f"Sent message to topic '{topic}': {message}")

    async def stop(self) -> None:
        """
        프로듀서를 종료합니다.
        """
        if self.producer:
            await self.producer.stop()
            logger.debug("aiokafka Producer stopped.")


class AioKafkaConsumerClient:
    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        group_id: Optional[str] = None,
        auto_offset_reset: str = "earliest",
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        """
        aiokafka 컨슈머 초기화

        :param bootstrap_servers: Kafka 브로커 주소 (예: "localhost:9092")
        :param topic: 구독할 토픽
        :param group_id: 컨슈머 그룹 ID (옵션)
        :param auto_offset_reset: 오프셋 초기화 정책 ("earliest" 또는 "latest")
        :param loop: asyncio 이벤트 루프 (기본값은 현재 이벤트 루프)
        """
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.auto_offset_reset = auto_offset_reset
        self.loop = loop or asyncio.get_event_loop()
        self.consumer: Optional[AIOKafkaConsumer] = None
        self._consume_task: Optional[asyncio.Task] = None

    async def start(self, callback: Callable[[Any], None]) -> None:
        """
        컨슈머를 시작하고, 별도의 태스크에서 메시지를 처리합니다.
        :param callback: 수신 메시지를 처리할 콜백 함수. 인자로 메시지 값(딕셔너리)을 받습니다.
        """
        self.consumer = AIOKafkaConsumer(
            self.topic,
            loop=self.loop,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            auto_offset_reset=self.auto_offset_reset,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )
        await self.consumer.start()
        logger.debug(f"aiokafka Consumer subscribed to topic '{self.topic}'")
        self._consume_task = self.loop.create_task(self._consume_loop(callback))

    async def _consume_loop(self, callback: Callable[[Any], None]) -> None:
        """
        내부 컨슈머 루프로, 콜백 함수를 호출해 메시지를 처리합니다.
        """
        try:
            async for msg in self.consumer:
                logger.debug(f"Received message from topic '{msg.topic}': {msg.value}")
                try:
                    callback(msg.value)
                except Exception as e:
                    logger.exception(f"Error processing message: {e}")
        except Exception as e:
            logger.exception(f"Consumer loop error: {e}")
        finally:
            await self.stop()
            logger.debug("Consumer loop terminated.")

    async def stop(self) -> None:
        """
        컨슈머를 종료하고 태스크를 취소합니다.
        """
        if self.consumer:
            await self.consumer.stop()
            logger.debug("aiokafka Consumer stopped.")
        if self._consume_task:
            self._consume_task.cancel()
            try:
                await self._consume_task
            except asyncio.CancelledError:
                logger.debug("Consumer task cancelled.")
