from hypurrquant_fastapi_core.logging_config import configure_logging
from hypurrquant_fastapi_core.response import BaseResponse
from hypurrquant_fastapi_core.api.exception import get_exception_by_code
from hypurrquant_fastapi_core.exception import (
    BaseOrderException,
    UnhandledErrorException,
    NonJsonResponseIgnoredException,
)
import aiohttp
import asyncio
from typing import Any, Dict, Optional

logger = configure_logging(__name__)

import asyncio

# 전역 카운터 & 락
_consecutive_html_count = 0
_html_count_lock = asyncio.Lock()


async def _increment_html_counter_and_maybe_raise():
    """
    text/html 응답이 올 때마다 카운터를 올리고,
    5회 연속이면 예외를 던짐.
    """
    global _consecutive_html_count
    async with _html_count_lock:
        _consecutive_html_count += 1
        if _consecutive_html_count >= 5:
            # 5회째에만 예외 발생
            _consecutive_html_count = 0
            raise Exception("5번 연속으로 비(非)JSON(text/html) 응답을 받았습니다.")


def _reset_html_counter():
    """JSON 응답이 오면 카운터 초기화"""
    global _consecutive_html_count
    _consecutive_html_count = 0


def log_request_error(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]],
    params: Optional[Dict[str, str]],
    data: Optional[Any],
    json_data: Optional[Dict[str, Any]],
    error: Exception,
    response: Optional[aiohttp.ClientResponse] = None,
) -> None:
    log_msg = (
        f"요청 실패 - Method: {method}, URL: {url}, Headers: {headers}, "
        f"Params: {params}, Data: {data}, JSON: {json_data}\n"
    )
    if response:
        log_msg += (
            f"Response Status: {response.status}, "
            f"Response Headers: {response.headers}, "
            f"Response Content-Type: {response.content_type}"
        )
    logger.info(log_msg, exc_info=True)


async def send_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, str]] = None,
    data: Optional[Any] = None,
    json: Optional[Dict[str, Any]] = None,
    timeout: int = 10,
) -> BaseResponse:

    async with aiohttp.ClientSession() as session:
        try:
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as response:

                # 1) Content-Type 검사
                content_type = response.headers.get("Content-Type", "")
                if "application/json" not in content_type:
                    # JSON이 아니면 카운터 올리고 5회 연속 시 예외
                    await _increment_html_counter_and_maybe_raise()
                    # 5회 미만인 동안엔 그냥 로그만 찍고 끝냄
                    body = await response.text()
                    logger.info(
                        f"Non-JSON response ignored (count<{_consecutive_html_count}>): "
                        f"status={response.status}, content-type={content_type}, body={body[:200]} count={_consecutive_html_count}"
                    )
                    raise NonJsonResponseIgnoredException("비정상적인 응답입니다.")

                # 2) JSON 응답이면 카운터 리셋
                _reset_html_counter()

                # 3) HTTP 오류 상태코드(4xx/5xx) 처리
                if response.status >= 400:
                    response_body = await response.json()
                    code = response_body.get("code")

                    if code is None:
                        raise UnhandledErrorException(
                            "400에러이지만 정의되지 않은 에러입니다."
                        )

                    message = response_body.get("message", "알 수 없는 오류")
                    raise BaseOrderException(message, code, status_code=response.status)

                # 4) 정상 JSON 파싱
                response_body = await response.json()
                return BaseResponse(**response_body)

        # 이하 기존 예외 핸들러 유지...
        except aiohttp.ClientConnectionError as e:
            logger.error("연결 오류 발생: 서버와의 연결에 실패했습니다.", exc_info=True)
            log_request_error(method, url, headers, params, data, json, e)
            raise e

        except asyncio.TimeoutError as e:
            logger.error(
                "타임아웃 오류 발생: 요청 시간이 초과되었습니다.", exc_info=True
            )
            log_request_error(method, url, headers, params, data, json, e)
            raise e

        except BaseOrderException:
            # 주문 오류는 이미 메시지 담겨 있으므로 그대로
            raise

        except Exception as e:
            logger.error(f"예상치 못한 오류 발생: {e}", exc_info=True)
            log_request_error(method, url, headers, params, data, json, e)
            raise


async def send_request_for_external(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, str]] = None,
    data: Optional[Any] = None,
    json: Optional[Dict[str, Any]] = None,
    timeout: int = 10,
) -> Dict[str, Any]:
    """
    비동기 HTTP 요청을 보내는 재사용 가능한 함수.

    Args:
        method (str): HTTP 메서드 (GET, POST, PUT 등).
        url (str): 요청 URL.
        headers (Optional[Dict[str, str]]): 요청 헤더.
        params (Optional[Dict[str, str]]): URL 쿼리 파라미터.
        data (Optional[Any]): 요청 바디 (form data 등).
        json (Optional[Dict[str, Any]]): 요청 바디 (JSON 데이터).
        timeout (int): 요청 타임아웃 (초 단위).

    Returns:
        Dict[str, Any]: JSON 응답 데이터.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as response:
                response_body = None
                response_body = await response.json()
                return response_body

        except aiohttp.ClientConnectionError as e:
            logger.error("연결 오류 발생: 서버와의 연결에 실패했습니다.", exc_info=True)
            log_request_error(method, url, headers, params, data, json, e)
            raise e
        except aiohttp.ClientResponseError as e:
            logger.error("응답 오류 발생: 잘못된 응답을 받았습니다.", exc_info=True)
            log_request_error(method, url, headers, params, data, json, e)
            raise e
        except aiohttp.ClientPayloadError as e:
            logger.error(
                "페이로드 오류 발생: 응답 페이로드 처리 중 문제가 발생했습니다.",
                exc_info=True,
            )
            log_request_error(method, url, headers, params, data, json, e)
            raise e
        except asyncio.TimeoutError as e:
            logger.error(
                "타임아웃 오류 발생: 요청 시간이 초과되었습니다.", exc_info=True
            )
            log_request_error(method, url, headers, params, data, json, e)
            raise e
        except aiohttp.ClientError as e:
            logger.error(f"기타 클라이언트 오류 발생: {str(e)}", exc_info=True)
            log_request_error(method, url, headers, params, data, json, e)
            raise e
        except Exception as e:
            logger.error(f"예상치 못한 오류 발생: {str(e)}", exc_info=True)
            log_request_error(method, url, headers, params, data, json, e)
            raise e
