from hypurrquant_fastapi_core.exception.base import BaseOrderException


class CopytradingServerException(BaseOrderException):  # 5000번대 에러
    pass


class CannotAcquireLockException(CopytradingServerException):
    """
    구독 요청 처리 중 락을 획득하지 못한 경우 발생하는 예외입니다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 5000, api_response)


class SubscribeFailException(CopytradingServerException):
    """
    구독 요청 처리 중 에러가 발생한 경우 발생하는 예외입니다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 5001, api_response)


class NoSuchSubscriptionException(CopytradingServerException):
    """
    구독이 존재하지 않는 경우 발생하는 예외입니다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 5002, api_response)


class CannotDeleteSubscriptionException(CopytradingServerException):
    """
    구독 삭제 요청 처리 중 에러가 발생한 경우 발생하는 예외입니다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 5003, api_response)


class NotCopyTradingAccountException(CopytradingServerException):
    """
    CopyTrading 계좌가 아닌 경우 발생한다.
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 5004, api_response)


class MaxCopyReachException(CopytradingServerException):
    """
    최대 Copy 수에 도달한 경우 발생한다.
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 5005, api_response)


class InvalidEthAddressException(CopytradingServerException):
    """
    올바르지 못 한 eth address인 경우 발생한다.
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 5006, api_response)


class MaxTargetReachedException(CopytradingServerException):
    """
    최대 Copy 수에 도달한 경우 발생한다.
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 5007, api_response)


class MaxSubscriptionReachedException(CopytradingServerException):
    """
    최대 구독 수에 도달한 경우 발생한다.
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 5008, api_response)
