from hypurrquant_fastapi_core.exception.base import BaseOrderException


class DcaServerException(BaseOrderException):  # 6000번대 에러
    pass


class DuplicationDcaException(DcaServerException):
    """
    DCA 주문이 중복된 경우 발생하는 예외입니다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 6000, api_response)


class CannotCreateMoreDcaException(DcaServerException):
    """
    DCA 주문이 최대 개수를 초과한 경우 발생하는 예외입니다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 6001, api_response)
