import os
import logging
import contextvars
import uuid
import functools
import asyncio
from slack_sdk import WebClient
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
import traceback
from pythonjsonlogger import jsonlogger

# contextvars를 사용하여 코루틴별 ID 저장
coroutine_id = contextvars.ContextVar("coroutine_id", default="N/A")


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
        # 기본 날짜 및 시간, 로거 관련 정보를 포맷팅
        # basic_info = f"`Environment`:  - {record.name} [PID: {record.process}, TID: {record.thread}, FUNC: {record.funcName}, LINE: {record.lineno}, COROUTINE_ID: {record.coroutine_id}]"
        # 1. 서버 이름
        error_weight = f"`Error Type`: {record.levelname}"
        server_info = f"`Server Name`: {self.server_name}"
        time_info = f"`Time`: {self.formatTime(record, self.datefmt)}"
        file_info = f"`File`: {record.name}"
        func_info = f"`Function`: {record.funcName}"
        environment_info = f"`Environment`: [PID: {record.process}, TID: {record.thread}, LINE: {record.lineno} COROUTINE_ID: {record.coroutine_id}]"
        # 2. 에러 무게 (레벨 이름과 번호)
        # 4. 메시지
        message = f"`Message`: {record.getMessage()}"
        # 5. 예외 정보 (있다면 삼중 backticks로 감싸기)
        exception_info = ""
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            exception_info = f" `Exception`\n```{exc_text}```"

        # 각 항목을 "|" 기호로 한 줄에 모두 연결 (번호별 네이밍)
        formatted = "\n\n".join(
            [
                server_info,
                error_weight,
                time_info,
                file_info,
                func_info,
                environment_info,
                message,
                exception_info,
            ]
        )
        return formatted


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
                print("Async loop is running, sending message asynchronously.")
                loop.create_task(self.async_send(msg))
            else:
                # 이벤트 루프가 없으면 동기 방식으로 전송
                self.sync_client.chat_postMessage(
                    channel=self.channel, text=msg, blocks=self._create_blocks(msg)
                )
        except SlackApiError as e:
            print(f"Slack API error: {e.response['error']}")
        except Exception as e:
            print(f"Unexpected error sending Slack message: {e}")

    async def async_send(self, msg):
        try:
            await self.async_client.chat_postMessage(
                channel=self.channel, text=msg, blocks=self._create_blocks(msg)
            )
        except SlackApiError as e:
            print(f"Async Slack API error: {e.response['error']}")
        except Exception as e:
            print(f"Unexpected async error: {e}")

    def _create_blocks(self, msg):
        # Slack 블록 포맷팅을 위한 메서드 (필요시 구현)
        return [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "💣 ERROR ALERT"},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": msg,
                },
            },
        ]


def configure_logging(file_path):
    """
    로깅 설정 함수. 파일 이름에 따라 핸들러가 동적으로 추가됩니다.
    :param file_path: 호출 파일 경로
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # 콘솔 핸들러 설정 (DEBUG 레벨 이상 처리)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logger_level)

    # JSON 포맷터 설정: 원하는 필드를 포함하도록 포맷 문자열 작성
    log_format = (
        "%(asctime)s %(name)s %(levelname)s %(message)s "
        "[PID: %(process)d, TID: %(thread)d, FUNC: %(funcName)s, LINE: %(lineno)d, COROUTINE_ID: %(coroutine_id)s]"
    )
    json_formatter = jsonlogger.JsonFormatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
    console_handler.setFormatter(json_formatter)
    console_handler.addFilter(CoroutineFilter())

    # Slack 핸들러 설정 (이전 코드와 동일)
    server_name = os.getenv("SERVER_NAME", "UnknownServer")
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    slack_channel = os.getenv("SLACK_CHANNEL")
    slack_handler = None
    if slack_token and slack_channel and server_name:
        slack_handler = SlackHandler(
            token=slack_token, channel=slack_channel, level=logging.ERROR
        )
        slack_formatter = SlackFormatter(
            server_name=server_name, datefmt="%Y-%m-%d %H:%M:%S"
        )
        slack_handler.setFormatter(slack_formatter)
        slack_handler.addFilter(CoroutineFilter())

    # 로거 생성 (호출 파일명을 로거 이름으로 사용)
    logger = logging.getLogger(file_path)
    logger.setLevel(logger_level)
    logger.addHandler(console_handler)
    if slack_handler:
        logger.addHandler(slack_handler)

    return logger


def coroutine_logging(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # 함수 실행 전에 고유한 UUID를 할당
        coroutine_id.set(str(uuid.uuid4()))
        return await func(*args, **kwargs)

    return wrapper


# 사용 예시
if __name__ == "__main__":
    logger = configure_logging(__file__)
    logger.info("This is an info message.")

    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("An error occurred!")
