from hypurrquant_fastapi_core.logging_config import configure_logging

from hyperliquid.websocket_manager import WebsocketManager
import asyncio
from typing import Any, Optional
import time
import websocket

logger = configure_logging(__name__)


def identifier_to_subscription(identifier: str) -> dict:
    # identifier가 colon(:)을 포함하지 않는 경우 (고정된 타입)
    if identifier == "allMids":
        return {"type": "allMids"}
    elif identifier == "userEvents":
        return {"type": "userEvents"}
    elif identifier == "orderUpdates":
        return {"type": "orderUpdates"}

    # identifier에 콜론이 포함된 경우: 콜론 이후 내용을 파싱합니다.
    if identifier.startswith("l2Book:"):
        coin = identifier[len("l2Book:") :]
        return {"type": "l2Book", "coin": coin}
    elif identifier.startswith("trades:"):
        coin = identifier[len("trades:") :]
        return {"type": "trades", "coin": coin}
    elif identifier.startswith("userFills:"):
        user = identifier[len("userFills:") :]
        return {"type": "userFills", "user": user}
    elif identifier.startswith("candle:"):
        # candle identifier 예시: "candle:btc,1m"
        try:
            data = identifier[len("candle:") :]
            coin, interval = data.split(",", 1)
            return {"type": "candle", "coin": coin, "interval": interval}
        except ValueError:
            raise ValueError(f"Invalid candle identifier format: {identifier}")
    elif identifier.startswith("userFundings:"):
        user = identifier[len("userFundings:") :]
        return {"type": "userFundings", "user": user}
    elif identifier.startswith("userNonFundingLedgerUpdates:"):
        user = identifier[len("userNonFundingLedgerUpdates:") :]
        return {"type": "userNonFundingLedgerUpdates", "user": user}
    else:
        raise ValueError(f"Unknown subscription identifier: {identifier}")


class ReconnectableWebsocketManager(WebsocketManager):
    def __init__(self, base_url: str, *args, **kwargs):
        # base_url을 별도로 저장하여 재연결 시 사용합니다.
        self.base_url = base_url
        super().__init__(base_url, *args, **kwargs)
        self.ws.on_close = self.on_close
        self.ws.on_error = self.on_error

    def on_open(self, _ws):
        logger.debug("on_open")
        self.ws_ready = True
        # 구독 큐에 있는 모든 요청을 구독 처리하고 active_subscriptions로 이동
        for subscription, active_subscription in self.queued_subscriptions:
            self.subscribe(
                subscription,
                active_subscription.callback,
                active_subscription.subscription_id,
            )
        self.queued_subscriptions.clear()

    def _reconnect(self):
        self.ws_ready = False
        # 활성화된 구독들을 모두 재구독 큐로 이동
        for identifier, active_subscriptions in self.active_subscriptions.items():
            subscription = identifier_to_subscription(identifier)
            for active_subscription in active_subscriptions:
                self.subscribe(
                    subscription,
                    active_subscription.callback,
                    active_subscription.subscription_id,
                )
        self.active_subscriptions.clear()

    def on_close(self, ws, close_status_code, close_msg):
        logger.warning(
            "ReconnectableWebsocketManager on_close: %s - %s",
            close_status_code,
            close_msg,
        )
        self._reconnect()

    def on_error(self, ws, error):
        logger.error("ReconnectableWebsocketManager on_error: %s", error)
        self._reconnect()

    def run(self):
        # 기존 ping_sender 스레드는 그대로 사용합니다.
        self.ping_sender.start()
        # 재연결을 위해 무한 루프로 실행합니다.
        while True:
            logger.info("ReconnectableWebsocketManager connecting...")
            self.ws.run_forever(ping_timeout=15, ping_interval=30)
            logger.info(
                "ReconnectableWebsocketManager disconnected. Reconnecting in 5 seconds..."
            )
            time.sleep(5)
            # 재연결을 위해 새 WebSocketApp 인스턴스를 생성하고
            # on_message, on_open은 부모(WebsocketManager) 그대로 사용하며,
            # on_close, on_error는 서브클래스의 메서드로 재할당합니다.
            ws_url = "ws" + self.base_url[len("http") :] + "/ws"
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_message=self.on_message,
                on_open=self.on_open,
                on_close=self.on_close,
                on_error=self.on_error,
            )


class AsyncWebsocketManager(ReconnectableWebsocketManager):
    """
    기존 WebSocketManager를 상속받아, 콜백 함수가 비동기인 경우
    메인 이벤트 루프에서 실행되도록 asyncio.run_coroutine_threadsafe()를 사용하며,
    on_close, on_error 이벤트에서 무조건 재연결(reconnect)하도록 구현합니다.
    """

    def __init__(self, base_url: str, *args, **kwargs):
        # base_url을 별도로 저장하여 재연결 시 사용합니다.
        self.base_url = base_url
        super().__init__(base_url, *args, **kwargs)
        # WebsocketManager에서는 on_close, on_error 콜백이 등록되어 있지 않으므로 여기서 재할당합니다.
        self.main_loop = asyncio.get_event_loop()

    def subscribe(
        self, subscription: dict, callback: Any, subscription_id: Optional[int] = None
    ) -> int:
        def async_callback(ws_msg):
            coro = callback(ws_msg)
            if asyncio.iscoroutine(coro):
                asyncio.run_coroutine_threadsafe(coro, self.main_loop)

        return super().subscribe(subscription, async_callback, subscription_id)
