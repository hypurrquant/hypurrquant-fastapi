from hypurrquant_fastapi_core.logging_config import configure_logging
import asyncio
import signal
from abc import ABC, abstractmethod
from typing import Any

logger = configure_logging(__name__)


class GracefulShutdownMixin(ABC):
    """
    최소 스펙 GracefulShutdown Mixin (루프 제어 포함)
    - run(): 시그널 등록 + 루프 제어
    - run_once(): 서브클래스가 구현할 '한 번의 작업'
    - is_stopped(), shutdown(): 중단 플래그 접근
    """

    def __init__(self, *args: Any, **kwargs: Any):
        self._stop_event = asyncio.Event()
        super().__init__(*args, **kwargs)

    async def init_signals(self) -> None:
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, self._stop_event.set)
        loop.add_signal_handler(signal.SIGTERM, self._stop_event.set)

    async def run(self, interval: float = 1.0) -> None:
        """
        1) 시그널 등록(init_signals)
        2) while 루프 제어(중단 체크, 인터벌 대기)
        3) run_once() 호출 반복
        """
        await self.init_signals()
        while not self._stop_event.is_set():
            try:
                await self.run_once()
            except Exception as e:
                # run_once에서 발생한 예외는 로깅하거나 처리할 수 있음
                logger.exception("Error in run_once")
            # interval 중에도 중단 신호를 기다림
            try:
                logger.debug(f"Waiting for {interval} seconds before next run...")
                await asyncio.wait_for(self._stop_event.wait(), timeout=interval)
            # 중단 신호가 발생하면 루프를 종료
            except asyncio.TimeoutError:
                continue
        logger.debug("Graceful shutdown initiated, exiting run loop.")

    @abstractmethod
    async def run_once(self) -> None:
        """
        서브클래스가 구현해야 하는 '한 번의 작업'.
        루프나 중단 체크 코드를 절대 포함하지 마세요.
        """
        ...

    def is_stopped(self) -> bool:
        return self._stop_event.is_set()

    def shutdown(self) -> None:
        self._stop_event.set()
