from hypurrquant_fastapi_core.logging_config import configure_logging
from hypurrquant_fastapi_core.api.async_http import send_request_for_external
from hypurrquant_fastapi_core.rate_limited import (
    hl_rate_limited,
    _default_async_limiter,
)
from hypurrquant_fastapi_core.messaging.client import AsyncMessagingConsumer
from hypurrquant_fastapi_core.constant.projects import HYPERLIQUID_API_URL
from hypurrquant_fastapi_core.singleton import singleton
from hypurrquant_fastapi_core.messaging.core import BaseConsumer
from hypurrquant_fastapi_core.utils.redis_config import redis_client
from hypurrquant_fastapi_core.constant.redis import DataRedisKey
import time
import asyncio
import json

logger = configure_logging(__name__)


@singleton
class CandleDataFetcher:
    def __init__(self):
        self.base_url = f"{HYPERLIQUID_API_URL}/info"
        self.headers = {"Content-Type": "application/json"}

    @hl_rate_limited(20)
    async def fetch_candle_data(self, coin, interval, start_time, end_time):
        """Fetch candle data for a specific coin and interval."""
        current_timestamp = int(time.time()) * 1000
        payload = {
            "type": "candleSnapshot",
            "req": {
                "coin": coin,
                "interval": interval,
                "startTime": start_time,
                "endTime": end_time,
            },
        }
        data = await send_request_for_external(
            "POST", self.base_url, self.headers, json=payload
        )
        if data is None or not isinstance(data, list):  # Check if the data is valid
            logger.exception(f"No data for {coin} with interval {interval}.")
            return None
        return data


@singleton
class DelegateResolver(BaseConsumer):
    def __init__(self, min_quota=600):
        BaseConsumer.__init__(
            self, "hypurrquant_common_delegate.fifo", 1, enable_deduplication=True
        )
        self.fetcher = CandleDataFetcher()
        self.min_quota = min_quota
        self.headers = {"Content-Type": "application/json"}

    async def process(self, data: dict, consumer: AsyncMessagingConsumer):
        """
        메시지를 처리하는 메서드.
        메시지의 'name' 필드에 따라 다른 작업을 수행합니다.
        """
        logger.debug(f"[{self.TOPIC}] Received message: {data}")
        quota = await _default_async_limiter.get_quota()
        logger.debug(
            f"[{self.TOPIC}] Current quota: {quota}. Min quota: {self.min_quota}."
        )
        if quota < self.min_quota:
            logger.warning(
                f"[{self.TOPIC}] Rate limit exceeded. Quota: {quota}. Waiting for reset."
            )
            await consumer.cancel()
            await consumer.pause()
            asyncio.create_task(self.resume(consumer))
            return

        name = data.get("name")
        logger.debug(f"[{self.TOPIC}] Processing message: {name}")

        if name == "fetch_candle":
            payload = data.get("data")
            start_ms = int(payload.get("start_ms"))
            end_ms = int(payload.get("end_ms"))
            ticker = payload.get("ticker")
            interval = payload.get("interval")
            ttl = int(payload.get("ttl", 600))
            response = await self.fetcher.fetch_candle_data(
                ticker, interval, start_ms, end_ms
            )
            if not response:
                logger.error(
                    f"[{self.TOPIC}] Failed to fetch candle data for {ticker} with interval {interval}."
                )
                return
            key = DataRedisKey.CANDLE_BY_TICKER_INTERVAL.value.format(
                ticker=ticker, interval=interval
            )
            await redis_client.setex(key, ttl, json.dumps(response))
            logger.debug(
                f"[{self.TOPIC}] candle data for {ticker} with interval {interval} saved to Redis."
            )
