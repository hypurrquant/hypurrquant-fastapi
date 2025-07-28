from hypurrquant_fastapi_core.utils.redis_config import redis_client
from hypurrquant_fastapi_core.logging_config import configure_logging
from hypurrquant_fastapi_core.messaging.dependencies import get_producer, get_consumer
from hypurrquant_fastapi_core.graceful_shutdown import GracefulShutdownMixin
from hypurrquant_fastapi_core.messaging.client import *
from hypurrquant_fastapi_core.exception import *
import time
from typing import Optional, Any, Callable, List, Dict
from uuid import uuid4
from abc import ABC, abstractmethod
import asyncio
from collections.abc import Callable, Awaitable
from dataclasses import dataclass, asdict
from contextlib import nullcontext

# 1) 반환 타입을 나타내는 TypeVar를 선언

logger = configure_logging(__name__)


###############################
# Messaging 관련 인터페이스 및 클래스
###############################
@dataclass
class BaseEventMessage:
    """
    이벤트 메시지를 파싱한 결과를 저장하는 데이터 클래스입니다.
    """

    event_id: str  # 이벤트 고유 id
    data: dict  # 이벤트 데이터
    is_idempotent: bool  # 멱등성 여부
    timestamp: Optional[int]  # 이벤트 발생 시간 (초 단위, 선택적)


@dataclass
class RedisEventMessage(BaseEventMessage):
    """
    Redis에 저장된 이벤트 메시지를 나타내는 데이터 클래스입니다.
    """

    status_key: str  # 상태 키 (Redis hash 키로 사용, event_id 포함)


###############################
# 단일 실행 보장 인터페이스 및 구현
###############################
class EnsureSingleExecutionInterface(ABC):
    """
    단일 실행 보장 인터페이스

    - is_idempotent=True: 상태만 체크, 이미 완료면 바로 리턴
    - is_idempotent=False: 락과 상태 체크를 통해 단일 실행 보장
    """

    @abstractmethod
    async def ensure_single_production(self, msg: Any):
        """
        단일 실행을 보장하는 래퍼 메서드.
        """
        pass

    @abstractmethod
    async def ensure_single_execution(
        self,
        task_callable: Callable[[], Awaitable],
        **kwargs,
    ) -> Awaitable:
        """
        단일 실행을 보장하는 래퍼 메서드.
        """
        pass


class RedisEnsureSingleExecution(EnsureSingleExecutionInterface):
    """
    단일 실행 보장 로직 추상화

    - is_idempotent=True: 상태만 체크, 이미 완료면 바로 리턴
    - is_idempotent=False: 락과 상태 체크를 통해 단일 실행 보장
    """

    def __init__(
        self, redis_client=redis_client, lock_timeout: int = 60, status_ttl: int = 120
    ):
        self.redis_client = redis_client
        self.lock_timeout = lock_timeout  # 기본 락 타임아웃 (초)
        self.status_ttl = status_ttl  # 상태 키 TTL (초)

    async def ensure_single_production(self, msg: RedisEventMessage):
        await redis_client.hset(
            msg.status_key,
            mapping={
                "status": "assigned",
                "assigned_at": msg.timestamp,
                "payload": json.dumps(msg.data),
            },
        )
        await redis_client.expire(msg.status_key, self.status_ttl)

    async def ensure_single_execution(
        self,
        task_callable: Callable[..., Awaitable],
        **kwargs: Any,
    ) -> None:
        """
        단일 실행을 보장하는 래퍼 메서드.
        """
        msg = kwargs.get("data", {})
        consumer = kwargs.get("consumer")
        event_message = RedisEventMessage(
            event_id=msg.get("event_id", ""),
            data=msg.get("data", {}),
            is_idempotent=msg.get("is_idempotent", False),
            timestamp=msg.get("timestamp"),
            status_key=msg.get("status_key", ""),
        )
        key = event_message.status_key

        async def _mark_completed():
            await self.redis_client.hset(
                key,
                mapping={
                    "status": "completed",
                    "completed_at": int(time.time()),
                },
            )
            await self.redis_client.expire(key, self.lock_timeout)

        # 1) 이미 완료된 상태인지 체크
        existing = await self.redis_client.hgetall(key)
        if existing and existing.get(b"status") == b"completed":
            logger.debug(f"[{key}] 이미 완료된 작업, 스킵합니다.")
            return

        # 2) 비멱등인 경우 락을 걸고, 멱등인 경우 락 없이 바로 실행
        lock_ctx = (
            self.redis_client.lock(f"lock:{key}", timeout=self.lock_timeout)
            if not event_message.is_idempotent
            else nullcontext()
        )
        logger.debug(f"lock이 진짜 락인지 확인: {lock_ctx is not nullcontext}")
        async with lock_ctx:
            # 중복 검사 한 번 더 (락 안 쓰는 멱등 분기에도 안전)
            existing = await self.redis_client.hgetall(key)
            if existing and existing.get(b"status") == b"completed":
                logger.debug(f"[{key}] 락 획득 후에도 완료된 상태, 스킵합니다.")
                return

            # 3) 실제 작업
            await task_callable(event_message.data, consumer)

            # 4) 완료 마킹
            await _mark_completed()
            logger.debug(f"[{key}] 작업 완료, status=completed로 기록했습니다.")


###############################
# Producer 인터페이스 및 구현
###############################
class BaseProducer(GracefulShutdownMixin):
    """
    1) produce(): Kafka에 이벤트 발행, 트래킹용 Redis hash 생성(assigned→…)
    2) is_done(): Redis hash에서 status=="completed" 여부 확인
    3) cleanup(): 처리 완료된 hash 키 즉시 삭제
    """

    KEY_PREFIX = "hypurrquant:common:status_key"

    def __init__(
        self,
        # TODO producer가 module import 시점에 초기화가 되므로 fastapi처럼 서비스 코드가 wrapping 되면은 문제가 없지만 그렇지 않을 경우엔 get_producer로 생성되면 producer가 속한 loop와 실제 main event loop가 달라짐.
        producer: AsyncMessagingProducer = get_producer(),
        ensure_single_execution: Optional[
            EnsureSingleExecutionInterface
        ] = RedisEnsureSingleExecution(redis_client=redis_client, lock_timeout=60),
        redis_client=redis_client,
        on_stale_event: Optional[Callable[[str, Dict], Awaitable[None]]] = None,
    ):
        super().__init__()
        self.producer = producer
        self._instance_id = uuid4().hex
        self.ensure_single_execution = ensure_single_execution
        self.redis_client = redis_client
        self.pattern = f"{self.KEY_PREFIX}:{self._instance_id}:*"
        self.on_stale_event = on_stale_event

    def _make_status_key(self, event_id: str) -> str:
        # track 키를 메시지에 포함시켜 consumer→redis 트래킹에 사용
        return f"{self.KEY_PREFIX}:{self._instance_id}:{event_id}"

    async def produce(
        self,
        topic: str,
        payload: dict,
        is_idempotent: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> RedisEventMessage:
        event_id = uuid4().hex
        status_key = self._make_status_key(event_id)

        # 1) payload에 status_key 추가
        msg: RedisEventMessage = RedisEventMessage(
            event_id=event_id,
            data=payload,
            is_idempotent=is_idempotent,
            timestamp=int(time.time()),
            status_key=status_key,
        )

        # 2) Kafka에 발행
        await self.producer.send_message(topic, asdict(msg), *args, **kwargs)

        # 3) Redis에 상태 키 생성
        await self.ensure_single_execution.ensure_single_production(msg)

        return msg

    def monitor(
        self,
        interval_seconds: int = 10,  # TODO 나중에 시간 수정해야함
    ):
        asyncio.create_task(self.run(interval_seconds))

    async def run_once(self):
        batch_size = 100
        buffer = []

        async for key in self.redis_client.scan_iter(
            match=self.pattern, count=batch_size
        ):
            buffer.append(key)
            if len(buffer) >= batch_size:
                await self._process_key_batch(buffer)
                buffer.clear()

        if buffer:
            await self._process_key_batch(buffer)

    async def _process_key_batch(
        self,
        keys: List[str],
    ):
        """
        한 번에 keys 리스트에 대한 HGETALL을 파이프라이닝으로 실행하기 전,
        TYPE 커맨드로 Hash 타입 키만 골라냅니다.
        timestamp 기준으로 60초 초과된 것만 처리.
        """
        try:
            # 1) 모든 키에 대해 TYPE 명령 실행
            types: List[str] = await asyncio.gather(
                *(self.redis_client.type(key) for key in keys)
            )
            # 2) Hash 타입인 키만 필터링
            hash_keys = [k for k, t in zip(keys, types) if t == "hash"]
            if not hash_keys:
                return  # 처리할 Hash 키가 없으면 바로 종료

            # 3) Hash 키에 대해서만 HGETALL 파이프라인
            pipe = self.redis_client.pipeline()
            for key in hash_keys:
                pipe.hgetall(key)
            results = await pipe.execute()  # List[dict[field: bytes]]

            now = int(time.time())
            # 4) 기존 로직: 상태 체크, 만료·완료 키 정리, stale 이벤트 호출
            for key, raw_hash in zip(hash_keys, results):
                logger.debug(f"[{key}] 키 처리 시작")
                if not raw_hash:
                    logger.debug(f"[{key}] 키가 비어있음, 스킵합니다.")
                    continue

                status = raw_hash.get(b"status") or raw_hash.get("status")
                if status == "completed":
                    logger.debug(f"[{key}] 완료된 작업, 삭제합니다.")
                    await self.redis_client.delete(key)
                    continue

                ts_bytes = raw_hash.get(b"assigned_at") or raw_hash.get("assigned_at")
                ts = int(ts_bytes)
                age = now - ts
                if age > 60 and self.on_stale_event:
                    await self.on_stale_event(key, raw_hash)

        except Exception as e:
            logger.exception(
                f"BaseProducer 배치 작업중 예외 발생 {keys}: {e}", exc_info=True
            )


###############################
# Consumer 인터페이스 및 구현
###############################
class BaseConsumer:
    """
    공통 consumer 로직 추상화

    - consumer 인스턴스 생성, 시작, 메시지 처리, 재개, 종료 로직 포함
    - process 메서드는 각 consumer의 주문 처리 로직에 따라 서브클래스에서 구현
    """

    CONSUMERS = []

    def __init__(
        self,
        topic: str,
        consumer_size: int,
        enable_deduplication: bool = False,
        ensure_single_execution: Optional[
            EnsureSingleExecutionInterface
        ] = RedisEnsureSingleExecution(redis_client=redis_client, lock_timeout=60),
    ):
        if enable_deduplication and not ensure_single_execution:
            raise ValueError(
                "enable_deduplication=True일 때 event_parser를 제공해야 합니다."
            )
        self.TOPIC = topic
        self.consumer_size = consumer_size
        self.consumer_list: List[AsyncMessagingConsumer] = [
            get_consumer(self.TOPIC) for _ in range(self.consumer_size)
        ]
        self.ensure_single_execution = ensure_single_execution
        self.enable_deduplication = enable_deduplication

    async def start(self):
        tasks = [
            asyncio.create_task(self._consume(consumer))
            for consumer in self.consumer_list
        ]
        BaseConsumer.CONSUMERS.extend(self.consumer_list)
        await asyncio.gather(*tasks)

    async def _consume(self, consumer: AsyncMessagingConsumer):
        logger.debug(f"[{self.TOPIC}] Consumer 시작: {consumer}")
        await consumer.start()
        async for msg in consumer.consume_messages(max_number_of_messages=1):
            try:
                if self.enable_deduplication:
                    logger.debug(f"[{self.TOPIC}] 중복 방지 작업 수행")
                    await self.ensure_single_execution.ensure_single_execution(
                        self.process,
                        data=msg,
                        consumer=consumer,
                    )
                else:
                    logger.debug(f"[{self.TOPIC}] 일반 작업 수행")
                    await self.process(msg["data"], consumer)
            except ApiLimitExceededException as e:
                # API Limit 초과 발생 시 1분 후 consumer 재개
                asyncio.create_task(self.resume(consumer))
            except Exception as e:
                logger.exception(
                    f"[{self.TOPIC}] 처리 중 정의되지 않은 에러 발생", exc_info=True
                )

    # TODO 추후에 모든 consumer를 일괄적으로 재개하는 로직을 구현할 수 있음
    # TODO sleep time을 인자로 받아야함.
    async def resume(self, consumer):
        await asyncio.sleep(60)
        await consumer.resume()

    @abstractmethod
    async def process(self, data: dict, consumer):
        """
        각 consumer 별 주문 처리 로직을 구현해야 합니다.
        """
        pass

    @classmethod
    async def stop_all_consumers(cls):
        """
        모든 consumer를 종료합니다.
        """
        for consumer in cls.CONSUMERS:
            await consumer.stop()
        cls.CONSUMERS = []
