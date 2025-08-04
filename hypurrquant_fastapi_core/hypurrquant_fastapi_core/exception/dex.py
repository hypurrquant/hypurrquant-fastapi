from hypurrquant_fastapi_core.exception.base import BaseOrderException


class DexException(BaseOrderException):
    pass


class NoSuchPoolException(DexException):
    """
    DEX에서 해당 풀을 찾을 수 없는 경우 발생한다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 8000, api_response)


class NoSuchDexException(DexException):
    """
    DEX가 존재하지 않는 경우 발생한다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 8001, api_response)


class NoLpVaultJobException(DexException):
    """
    DEX LP Vault Job이 존재하지 않는 경우 발생한다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 8002, api_response)


class NoSuchDexProtocolException(DexException):
    """
    지원하지 않는 DEX 프로토콜인 경우 발생한다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 8003, api_response)


class DecreaseLiquidityException(DexException):
    """
    DEX에서 유동성 감소 작업이 실패한 경우 발생한다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 8004, api_response)
