import time
import asyncio
from collections import deque
from functools import wraps
from typing import Callable, Deque, Tuple, Any, Coroutine


class AsyncRateLimiter:
    def __init__(self, max_quota: int = 1200, window_sec: int = 60):
        self.max_quota = max_quota
        self.window = window_sec
        self.history: Deque[Tuple[float, int]] = deque()
        self._lock = asyncio.Lock()

    async def _cleanup(self) -> None:
        """윈도우 밖의 오래된 기록을 제거."""
        now = time.monotonic()
        cutoff = now - self.window
        while self.history and self.history[0][0] <= cutoff:
            self.history.popleft()

    async def record(self, weight: int = 1) -> int:
        """
        weight만큼 기록하고, 기록 후 현재 총 사용량을 반환합니다.
        """
        async with self._lock:
            await self._cleanup()
            self.history.append((time.monotonic(), weight))
            return sum(w for _, w in self.history)

    async def get_quota(self) -> int:
        """
        현재 남은 허용량을 반환합니다.
        """
        async with self._lock:
            await self._cleanup()
            used = sum(w for _, w in self.history)
            return max(0, self.max_quota - used)


# 전역으로 하나만 생성
_default_async_limiter = AsyncRateLimiter(max_quota=1200, window_sec=60)


def hl_rate_limited(
    weight: int = 1, limiter: AsyncRateLimiter = _default_async_limiter
):
    """
    async 함수용 레이트 리밋 데코레이터.
    허용량 초과 시 RuntimeError 발생.
    """

    def decorator(
        fn: Callable[..., Coroutine[Any, Any, Any]],
    ) -> Callable[..., Coroutine[Any, Any, Any]]:
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            try:
                result = await fn(*args, **kwargs)
                return result
            finally:
                await limiter.record(weight)

        return wrapper

    return decorator
