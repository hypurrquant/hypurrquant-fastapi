from hypurrquant_fastapi_core.logging_config import (
    configure_logging,
)
from hypurrquant_fastapi_core.singleton import singleton
from types_aiobotocore_sqs.client import SQSClient
from contextlib import asynccontextmanager
import botocore.exceptions
import asyncio
import json
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from abc import ABC, abstractmethod
import aioboto3
from typing import Any
import uuid

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
    async def send_message(self, destination, message: Any, *args, **kwargs):
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

    async def send_message(self, destination: str, message: Any, *args, **kwargs):
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
        if self.client is None:
            logger.info("Starting SQS client")
            self.client = await self.session.client(
                "sqs", region_name=self.region_name
            ).__aenter__()
            logger.info("SQS client started")

    async def stop(self):
        if self.client:
            logger.info("Stopping SQS client")
            await self.client.__aexit__(None, None, None)
            self.client = None

    async def _reconnect(self):
        logger.warning("Reconnecting SQS client due to error...")
        await self.stop()
        # 약간의 대기 후 재시도 (네트워크 상황에 따라 조정 가능)
        await asyncio.sleep(1)
        await self.start()

    async def send_message(
        self,
        destination: str,
        message: Any,
        *args,
        **kwargs,
    ):
        message_group_id = kwargs.get("message_group_id", "default-group")
        try:
            if "fifo" in destination:
                # FIFO 큐인 경우 MessageGroupId와 MessageDeduplicationId 필요
                await self.client.send_message(
                    QueueUrl=destination,
                    MessageBody=json.dumps(message),
                    MessageGroupId=message_group_id,
                    MessageDeduplicationId=str(uuid.uuid4()),
                )
            else:
                await self.client.send_message(
                    QueueUrl=destination, MessageBody=json.dumps(message)
                )
        except botocore.exceptions.ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            logger.exception(f"ClientError in send_message")
            # 연결 문제 또는 클라이언트 만료와 관련된 에러라면 재연결 시도
            if error_code in (
                "RequestTimeout",
                "RequestTimeoutException",
                "ExpiredToken",
            ):
                await self._reconnect()
                # 재연결 후 재시도
                if "fifo" in destination:
                    # FIFO 큐인 경우 MessageGroupId와 MessageDeduplicationId 필요
                    await self.client.send_message(
                        QueueUrl=destination,
                        MessageBody=json.dumps(message),
                        MessageGroupId=message_group_id,
                        MessageDeduplicationId=str(uuid.uuid4()),
                    )
                else:
                    await self.client.send_message(
                        QueueUrl=destination, MessageBody=json.dumps(message)
                    )
            else:
                raise
        except Exception as e:
            logger.exception("Unexpected error in send_message")
            raise


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
    async def consume_messages(self, *args, **kwargs):
        """
        destination: Kafka에서는 topic, SQS에서는 큐 URL 등 (구현체에 따라 사용)
        async generator 형태로 메시지를 yield합니다.
        """
        pass

    @abstractmethod
    async def pause(self):
        """
        소비를 일시정지합니다.
        """
        pass

    @abstractmethod
    async def resume(self):
        """
        소비를 재개합니다.
        """
        pass

    async def cancel(self):
        """
        현재 처리 중인 메시지도 포함하여 이후 소비도 모두 취소합니다.
        이 메서드가 호출되면, 진행 중인 메시지의 처리가 끝난 후에도
        커밋(혹은 삭제)이 실행되지 않으므로, 해당 메시지들은 소비되지 않은 것으로 남습니다.
        """
        self._consume = False
        logger.info("Consumption canceled: 현재 및 이후 메시지 소비가 취소되었습니다.")


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
        # 자동 커밋 비활성화 후, 메시지 처리 성공 시 수동 커밋 수행
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )
        self._paused = asyncio.Event()  # 일시정지/재개 이벤트
        self._paused.set()  # 기본값은 재개 상태
        self._consume = True  # 소비 여부 플래그

    async def pause(self):
        """
        메시지 처리와 함께 fetch 단계도 일시정지하도록 Kafka consumer의 pause()를 호출합니다.
        """
        # 이미 일시정지 상태라면 아무것도 수행하지 않음
        if not self._paused.is_set():
            logger.info("Kafka Consumer is already paused. Skipping pause call.")
            return

        self._paused.clear()
        partitions = self.consumer.assignment()
        if partitions:
            self.consumer.pause(*partitions)
        logger.info("Kafka Consumer paused (fetch and processing paused).")

    async def resume(self):
        """
        메시지 처리와 fetch 단계 모두를 재개하도록 Kafka consumer의 resume()를 호출합니다.
        """
        # 이미 재개 상태라면 아무것도 수행하지 않음
        if self._paused.is_set():
            logger.info("Kafka Consumer is already resumed. Skipping resume call.")
            return

        self._paused.set()
        partitions = self.consumer.assignment()
        if partitions:
            self.consumer.resume(*partitions)
        logger.info("Kafka Consumer resumed (fetch and processing resumed).")

    async def start(self):
        await self.consumer.start()

    async def stop(self):
        await self.consumer.stop()

    @asynccontextmanager
    async def process_message(self, msg):
        """
        Kafka 메시지 처리 컨텍스트 매니저.
        블록 내에서 예외 없이 정상 처리된 경우,
        _consume 플래그가 활성화되어 있을 때만 오프셋을 커밋합니다.
        """
        try:
            yield msg.value  # 사용자에게 처리할 메시지 값을 전달
        except Exception:
            logger.exception("Error processing Kafka message")
            raise
        else:
            if self._consume:
                try:
                    await self.consumer.commit()
                    logger.debug("Kafka message committed successfully")
                except Exception as commit_error:
                    logger.exception("Error committing Kafka message: %s", commit_error)
            else:
                logger.info("Consumption canceled: Kafka message not committed.")
                self._consume = True  # 재설정하여 이후 메시지 소비 가능

    async def consume_messages(self, *args, **kwargs):
        """
        Kafka 메시지 소비 루프.
        _consume 플래그가 꺼지면 이후 메시지뿐만 아니라,
        현재 진행 중인 메시지도 정상 처리 후 커밋하지 않습니다.
        """
        try:
            async for msg in self.consumer:
                await self._paused.wait()
                try:
                    async with self.process_message(msg) as processed_value:
                        yield processed_value
                except Exception:
                    # 개별 메시지 처리 실패 시, 오프셋은 커밋되지 않으므로
                    # 동일 메시지가 재처리될 수 있습니다.
                    continue
        except Exception as e:
            logger.exception("Kafka Consumer error: %s", e)


class SQSMessagingConsumer(AsyncMessagingConsumer):
    def __init__(self, queue_url: str, region_name: str):
        self.queue_url = queue_url
        self.region_name = region_name
        self.session = aioboto3.Session()
        self.client = None
        self._paused = asyncio.Event()  # 일시정지/재개 이벤트
        self._paused.set()  # 기본값은 재개 상태
        self._consume = True  # 소비 여부 플래그

    async def pause(self):
        # 이미 일시정지 상태라면 아무것도 수행하지 않음
        if not self._paused.is_set():
            logger.info("SQS Consumer is already paused. Skipping pause call.")
            return

        self._paused.clear()
        logger.info("SQS Consumer paused.")

    async def resume(self):
        # 이미 재개 상태라면 아무것도 수행하지 않음
        if self._paused.is_set():
            logger.info("SQS Consumer is already resumed. Skipping resume call.")
            return

        self._paused.set()
        logger.info("SQS Consumer resumed.")

    async def start(self):
        logger.info("Starting SQS consumer client")
        self.client = await self.session.client(
            "sqs", region_name=self.region_name
        ).__aenter__()

    async def stop(self):
        if self.client:
            logger.info("Stopping SQS consumer client")
            await self.client.__aexit__(None, None, None)
            self.client = None

    async def _reconnect(self):
        logger.warning("Reconnecting SQS consumer client due to error...")
        await self.stop()
        await asyncio.sleep(1)
        await self.start()

    @asynccontextmanager
    async def process_message(self, message):
        """
        SQS 메시지 처리 컨텍스트 매니저.
        블록 내에서 예외 없이 정상 처리된 경우,
        _consume 플래그가 활성화되어 있을 때만 메시지를 삭제(커밋)합니다.
        """
        try:
            yield message
        except Exception:
            logger.exception("Error during SQS message processing")
            raise
        else:
            if self._consume:
                try:
                    await self.client.delete_message(
                        QueueUrl=self.queue_url, ReceiptHandle=message["ReceiptHandle"]
                    )
                    logger.debug("SQS message deleted (committed) successfully")
                except botocore.exceptions.ClientError as e:
                    logger.error(f"Error deleting SQS message: {e}")
                except Exception as e:
                    logger.exception("Unexpected error deleting SQS message")
            else:
                logger.info("Consumption canceled: SQS message not deleted.")
                self._consume = True

    async def consume_messages(self, *args, **kwargs):
        """
        SQS 메시지 소비 루프.
        _consume 플래그가 꺼지면 이후 메시지뿐만 아니라,
        현재 진행 중인 메시지도 정상 처리 후 삭제하지 않습니다.
        """
        while True:
            await self._paused.wait()
            try:
                max_number_of_messages = kwargs.get("max_number_of_messages", 10)
                response = await self.client.receive_message(
                    QueueUrl=self.queue_url,
                    MaxNumberOfMessages=max_number_of_messages,
                    WaitTimeSeconds=20,  # long polling
                )
            except botocore.exceptions.ClientError as e:
                error_code = e.response.get("Error", {}).get("Code")
                logger.error(f"ClientError in receive_message: {error_code} - {e}")
                if error_code in (
                    "RequestTimeout",
                    "RequestTimeoutException",
                    "ExpiredToken",
                ):
                    await self._reconnect()
                    continue
                else:
                    raise
            except Exception as e:
                logger.exception("Unexpected error during receive_message")
                await self._reconnect()
                continue

            messages = response.get("Messages", [])
            if messages:
                for m in messages:
                    if not self._consume:
                        logger.info(
                            "Consumption canceled during processing: breaking out."
                        )
                        break
                    try:
                        async with self.process_message(m) as msg:
                            yield json.loads(msg["Body"])
                    except Exception:
                        # 개별 메시지 처리 에러는 로깅하고 다음 메시지로 넘어갑니다.
                        continue

            await asyncio.sleep(0.1)
