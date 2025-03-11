from hypurrquant_fastapi_core.exception import (
    BaseOrderException,
    ApiLimitExceededException,
)
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from hypurrquant_fastapi_core.logging_config import configure_logging
from hypurrquant_fastapi_core.response import BaseResponse
from hyperliquid.utils.error import ClientError, ServerError
from pymongo.errors import PyMongoError
import aiohttp


logger = configure_logging(__name__)


# ================================
# 서버내 정의된 BaseOrderException 를 상속받은 예외를 처리
# ================================
async def base_order_exception_handler(request: Request, exc: BaseOrderException):
    logger.warning(f"BaseOrderException: {exc}", exc_info=True)
    response = BaseResponse(
        code=exc.code, data=exc.api_response, error_message=exc.message
    )
    return JSONResponse(status_code=exc.status_code, content=response.model_dump())


# ================================
# aiohttp 예외 처리
# ================================
async def aiohttp_ClientError_handler(request: Request, exc: aiohttp.ClientError):
    logger.error(f"aiohttp.ClientError: {exc}", exc_info=True)
    response = BaseResponse(code=503, data=None, error_message=str(exc))
    return JSONResponse(status_code=exc.status_code, content=response.model_dump())


# ================================
# API limit eror, 503 error를 내보냄
# ================================
async def api_limit_429_exception_handler(
    request: Request, exc: ApiLimitExceededException
):
    response = BaseResponse(
        code=exc.code, data=exc.api_response, error_message=exc.message
    )
    return JSONResponse(status_code=exc.status_code, content=response.model_dump())


# ================================
# monogodb 에러 처리
# ================================
async def pyMongoError_handler(request: Request, exc: PyMongoError):
    logger.error(f"PyMongoError: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=BaseResponse(
            code=502,
            error_message=str(exc),
        ).model_dump(),
    )


# ================================
# 다뤄지지 않은 Hyperliquid client error
# ================================
async def hypuerliquid_client_error_handler(
    request: Request, exc: ClientError
):  # TODO 나중에 ClientError, ServerError 반환 스펙 살펴보기
    logger.error(f"Unhandled Hyperliquid client error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content=BaseResponse(
            code=500,
            error_message=str(ClientError),
        ).model_dump(),
    )


# ================================
# Hyperliquid Server Error 처리
# ================================
async def hypuerliquid_server_error_handler(request: Request, exc: ServerError):
    logger.error(f"Unhandled Hyperliquid server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content=BaseResponse(code=501, error_message=str(exc)).model_dump(),
    )


# ================================
# 사용자의 요청이 올바르지 않은 경우
# ================================
async def request_validaiton_exception_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content=BaseResponse(
            code=422,
            data=None,  # 유효하지 않은 요청에는 데이터가 없음
            error_message="api 스펙에 맞지 않은 요청입니다.",
            message=str(exc.errors()),  # 에러 세부사항을 문자열로 변환
        ).dict(),  # Pydantic 모델을 JSON으로 직렬화
    )


# ================================
# 정의되지 않은 예외 처리
# ================================
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=BaseResponse(
            code=9999,
            data=None,
            error_message="정의되지 않은 예외가 발생했습니다. 당장 확인이 필요합니다.",
            message=str(exc),  # 예외 메시지를 출력
        ).dict(),
    )
