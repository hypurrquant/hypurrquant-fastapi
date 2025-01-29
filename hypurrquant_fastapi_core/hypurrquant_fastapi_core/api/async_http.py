import aiohttp
from typing import Any, Dict, Optional, Optional
from hypurrquant_fastapi_core.logging_config import configure_logging
from hypurrquant_fastapi_core.response import BaseResponse
from hypurrquant_fastapi_core.api.exception import get_exception_by_code
from hypurrquant_fastapi_core.exception import BaseOrderException

logger = configure_logging(__file__)


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
                        error_message = "서버의 응답을 처리하던 중 문제가 발생했습니다."
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

        except aiohttp.ClientError as e:
            return {"error": f"Request failed: {str(e)}"}


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

        except aiohttp.ClientError as e:
            logger.error(
                f"외부 서버에 요청을 보내던 중 aiohttp에서 문제가 발생했습니다: {e}"
            )
            raise e
