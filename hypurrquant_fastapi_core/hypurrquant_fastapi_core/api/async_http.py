from hypurrquant_fastapi_core.logging_config import configure_logging
from hypurrquant_fastapi_core.response import BaseResponse
from hypurrquant_fastapi_core.api.exception import get_exception_by_code
from hypurrquant_fastapi_core.exception import BaseOrderException
import aiohttp
import asyncio
from typing import Any, Dict, Optional

logger = configure_logging(__name__)


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
                response_body = await response.json()
                if response.status >= 400:
                    code = None
                    try:
                        code = response_body["code"]
                    except Exception as e:
                        error_message = "내부 서버에서 정의되지 않은 예외 코드가 발견되었습니다. 해당 예외를 살핀 후 수정해주세요"
                        logger.error(error_message)
                        logger.error(response_body)
                        raise Exception(error_message)

                    raise BaseOrderException(
                        response_body["message"],
                        response_body["code"],
                        status_code=response.status,
                    )
                else:
                    return BaseResponse(**response_body)

        except aiohttp.ClientConnectionError as e:
            logger.error("연결 오류 발생: 서버와의 연결에 실패했습니다.", exc_info=True)
            log_request_error(method, url, headers, params, data, json, e, response)
            raise e
        except aiohttp.ClientResponseError as e:
            logger.error("응답 오류 발생: 잘못된 응답을 받았습니다.", exc_info=True)
            log_request_error(method, url, headers, params, data, json, e, response)
            raise e
        except aiohttp.ClientPayloadError as e:
            logger.error(
                "페이로드 오류 발생: 응답 페이로드 처리 중 문제가 발생했습니다.",
                exc_info=True,
            )
            log_request_error(method, url, headers, params, data, json, e, response)
            raise e
        except asyncio.TimeoutError as e:
            logger.error(
                "타임아웃 오류 발생: 요청 시간이 초과되었습니다.", exc_info=True
            )
            log_request_error(method, url, headers, params, data, json, e, response)
            raise e
        except aiohttp.ClientError as e:
            logger.error(f"기타 클라이언트 오류 발생: {str(e)}", exc_info=True)
            log_request_error(method, url, headers, params, data, json, e, response)
            raise e
        except Exception as e:
            logger.error(f"예상치 못한 오류 발생: {str(e)}", exc_info=True)
            log_request_error(method, url, headers, params, data, json, e, response)
            raise e


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
