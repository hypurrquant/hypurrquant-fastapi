from hypurrquant_fastapi_core.exception.base import BaseOrderException


class CommonException(BaseOrderException):
    pass


class NonJsonResponseIgnoredException(CommonException):
    """
    JSON이 아닌 응답을 무시하는 경우 발생한다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 0, api_response)


class UnhandledErrorException(BaseOrderException):
    """
    buy, sell 주문에서 처리되지 않은 예외가 발생한 경우 발생한다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 9999, api_response)
