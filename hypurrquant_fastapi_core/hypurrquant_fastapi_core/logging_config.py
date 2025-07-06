import os
import logging
import contextvars
import uuid
import functools
import asyncio
from slack_sdk import WebClient
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from pythonjsonlogger import jsonlogger
import logging_loki
from multiprocessing import Queue
import sys

# contextvars를 사용하여 코루틴별 ID 저장
coroutine_id = contextvars.ContextVar("coroutine_id", default="N/A")


SERVER_NAME = os.getenv("SERVER_NAME", "UnknownServer")
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")
LOKI_URL = os.getenv("LOKI_URL")
PROFILE = os.getenv("PROFILE", "prod")


# 커스텀 로깅 필터
class CoroutineFilter(logging.Filter):
    def filter(self, record):
        record.coroutine_id = coroutine_id.get()
        return True


logger_level = os.getenv("LOG_LEVEL", "DEBUG").upper()
if isinstance(logger_level, int):
    logger_level = logging.getLevelName(logger_level)


# 커스텀 Slack Formatter
class SlackFormatter(logging.Formatter):
    def __init__(self, server_name, fmt=None, datefmt=None, style="%"):
        self.server_name = server_name
        # 기본 포맷 문자열은 빈 값으로 처리 (우리가 format() 메서드에서 직접 구성)
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def format(self, record):
        # 기본 정보 구성
        error_weight = f"`Error Type`: {record.levelname}"
        server_info = f"`Server Name`: {self.server_name}"
        time_info = f"`Time`: {self.formatTime(record, self.datefmt)}"
        file_info = f"`File`: {record.name}"
        func_info = f"`Function`: {record.funcName}"
        environment_info = f"`Environment`: [PID: {record.process}, TID: {record.thread}, LINE: {record.lineno} COROUTINE_ID: {record.coroutine_id}]"
        message = f"`Message`: {record.getMessage()}"

        # 기본 메시지에 예외 정보 없이 연결
        formatted = "\n\n".join(
            [
                server_info,
                error_weight,
                time_info,
                file_info,
                func_info,
                environment_info,
                message,
            ]
        )

        # 예외 정보가 있는 경우
        exception_parts = []
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            max_chunk = 2000
            # exc_text를 2000자씩 분할
            chunks = [
                exc_text[i : i + max_chunk] for i in range(0, len(exc_text), max_chunk)
            ]
            for idx, chunk in enumerate(chunks):
                if idx == 0:
                    # 첫번째 조각에는 제목을 포함
                    exception_parts.append(f"`Exception`\n```{chunk}```")
                else:
                    # 이후 조각은 제목 없이 추가
                    exception_parts.append(f"```{chunk}```")
            # 기본 메시지 뒤에 예외 부분 추가
        return [formatted] + exception_parts


# Slack 알림 전송용 커스텀 핸들러 (에러 수준 이상의 로그 전송)
class SlackHandler(logging.Handler):
    def __init__(self, token, channel, level=logging.ERROR):
        super().__init__(level)
        self.token = token
        self.channel = channel
        # 동기 클라이언트
        self.sync_client = WebClient(token=token)
        # 비동기 클라이언트
        self.async_client = AsyncWebClient(token=token)

    def emit(self, record):
        try:
            msg = self.format(record)
            # 현재 이벤트 루프가 있는지 확인
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                loop.create_task(self.async_send(msg))
            else:
                pass
        except SlackApiError as e:
            print(f"Slack API error: {e.response['error']}")
        except Exception as e:
            print(f"Unexpected error sending Slack message: {e}")

    async def async_send(self, msg):
        try:
            await self.async_client.chat_postMessage(
                channel=self.channel, text="error", blocks=self._create_blocks(msg)
            )
        except SlackApiError as e:
            print(f"Async Slack API error: {e.response['error']}")
        except Exception as e:
            print(f"Unexpected async error: {e}")

    def _create_blocks(self, msgs: list):
        # Slack 블록 포맷팅을 위한 메서드 (필요시 구현)
        block_list = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "💣 ERROR ALERT"},
            },
        ]

        for msg in msgs:
            block_list.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": msg,
                    },
                }
            )
        return block_list


def configure_logging(file_path):
    """
    로깅 설정 함수. 파일 이름에 따라 핸들러가 동적으로 추가됩니다.
    :param file_path: 호출 파일 경로
    """
    # log_dir = "logs"
    # if not os.path.exists(log_dir):
    #     os.makedirs(log_dir, exist_ok=True)

    # 콘솔 핸들러 설정 (DEBUG 레벨 이상 처리)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logger_level)

    # JSON 포맷터 설정: 원하는 필드를 포함하도록 포맷 문자열 작성
    log_format = (
        "%(asctime)s %(name)s %(levelname)s %(message)s "
        "[PID: %(process)d, TID: %(thread)d, FUNC: %(funcName)s, LINE: %(lineno)d, COROUTINE_ID: %(coroutine_id)s]"
    )
    json_formatter = jsonlogger.JsonFormatter(
        log_format, datefmt="%Y-%m-%d %H:%M:%S", json_ensure_ascii=False
    )
    console_handler.setFormatter(json_formatter)
    console_handler.addFilter(CoroutineFilter())

    # Slack 핸들러 설정 (이전 코드와 동일)
    slack_handler = None

    if SLACK_TOKEN and SLACK_CHANNEL and SERVER_NAME:
        slack_handler = SlackHandler(
            token=SLACK_TOKEN, channel=SLACK_CHANNEL, level=logging.WARNING
        )
        slack_formatter = SlackFormatter(
            server_name=SERVER_NAME, datefmt="%Y-%m-%d %H:%M:%S"
        )
        slack_handler.setFormatter(slack_formatter)
        slack_handler.addFilter(CoroutineFilter())

    if PROFILE == "prod" and not SLACK_TOKEN:
        raise ValueError("SLACK_BOT_TOKEN and SLACK_CHANNEL must be set in production")
    # 로키 설정
    loki_handler = None
    if LOKI_URL:
        loki_handler = logging_loki.LokiQueueHandler(
            Queue(-1),
            url=LOKI_URL,
            tags={"application": SERVER_NAME},
            version="1",
        )
        loki_handler.addFilter(CoroutineFilter())
        loki_handler.setFormatter(json_formatter)

    # 로거 생성 (호출 파일명을 로거 이름으로 사용)
    logger = logging.getLogger(file_path)
    logger.setLevel(logger_level)
    logger.addHandler(console_handler)
    if slack_handler:
        logger.addHandler(slack_handler)
    if loki_handler:
        logger.addHandler(loki_handler)

    return logger


def coroutine_logging(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # 이미 코루틴에서 UUID가 설정되어 있지 않은 경우에만 초기화
        if coroutine_id.get() == "N/A":
            coroutine_id.set(str(uuid.uuid4()))
        return await func(*args, **kwargs)

    return wrapper
