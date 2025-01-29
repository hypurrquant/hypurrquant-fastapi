from fastapi_core.exception import BaseOrderException, UnhandledErrorException


class ApiLimitExceededException(BaseOrderException):
    """
    API 요청 제한이 초과된 경우 발생한다.
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 3000, api_response, 503)


class NoSuchAccountByProvidedNickNameException(BaseOrderException):
    """
    주어진 닉네임의 계좌가 없다.
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 3003, api_response)


class NoSuchAccountByProvidedTelegramIdException(BaseOrderException):
    """
    주어진 텔레그램 계좌가 없다.
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 3004, api_response)


def get_exception_by_code(code: int) -> BaseOrderException:
    """
    에러 코드에 따라 적절한 예외를 반환하는 함수.

    Args:
        code (int): 상호 협의된 에러 코드.
        message (str): 에러 메시지.
        api_response (Optional[Any]): 관련된 추가 API 응답 데이터.

    Returns:
        ApiException: 적절한 예외 객체.
    """
    exception_mapping = {
        3000: ApiLimitExceededException,
        3003: NoSuchAccountByProvidedNickNameException,
        3004: NoSuchAccountByProvidedTelegramIdException,
        9999: UnhandledErrorException,  # Unhandled error
    }

    exception_class = exception_mapping.get(
        code, UnhandledErrorException
    )  # 기본값은 UnhandledErrorException
    return exception_class()  # 메시지를 전달하여 예외 생성
