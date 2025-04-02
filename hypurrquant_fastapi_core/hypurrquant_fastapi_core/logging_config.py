import logging
import os
import contextvars
import uuid
import functools

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


def configure_logging(file_path):
    """
    로깅 설정 함수. 파일 이름에 따라 파일 핸들러가 동적으로 추가됩니다.
    :param file_path: 호출 파일 경로
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # 콘솔 핸들러 설정 (DEBUG 레벨 이상 처리)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logger_level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s "
        "[PID: %(process)d, TID: %(thread)d, FUNC: %(funcName)s, LINE: %(lineno)d COROUTINE_ID: %(coroutine_id)s]"
    )
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(CoroutineFilter())

    # 로거 설정 (호출 파일명을 로거 이름으로 사용)
    logger = logging.getLogger(file_path)
    logger.setLevel(logger_level)
    logger.addHandler(console_handler)

    return logger


def coroutine_logging(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # 함수 실행 전에 고유한 UUID를 할당
        coroutine_id.set(str(uuid.uuid4()))
        return await func(*args, **kwargs)

    return wrapper
