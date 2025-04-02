import logging
import os

logger_level = os.getenv("LOG_LEVEL", "DEBUG").upper()
if isinstance(logger_level, int):
    logger_level = logging.getLevelName(logger_level)


def configure_logging(file_path):
    """
    로깅 설정 함수. 파일 이름에 따라 파일 핸들러가 동적으로 추가됩니다.
    :param file_path: 호출 파일 경로
    """
    # 호출 파일 이름에서 파일명을 추출
    # file_name = os.path.splitext(os.path.basename(file_path))[0]

    # 로그 디렉토리 설정 및 생성 (필요시)
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # 콘솔 핸들러 설정 (DEBUG 레벨만 처리)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logger_level)  # DEBUG 이상만 콘솔에 출력
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s [PID: %(process)d, TID: %(thread)d FUNC: %(funcName)s, LINE: %(lineno)d]"
    )
    console_handler.setFormatter(console_formatter)

    # 로깅 설정
    logger = logging.getLogger(file_path)  # 호출 파일 이름을 로거 이름으로 사용
    logger.setLevel(logger_level)  # 전체 로깅 레벨 설정
    logger.addHandler(console_handler)

    return logger
