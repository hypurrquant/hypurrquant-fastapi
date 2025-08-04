from hypurrquant_fastapi_core.exception.base import BaseOrderException


class OrderServerException(BaseOrderException):
    """
    주문 요청이 실패한 경우 발생한다.
    """

    pass


class InvalidSecretKeyInL1ChainException(OrderServerException):
    """
    응답에 err가 들어간 경우 발생한다.
    error_message: L1 error: User or API Wallet ~ does not exist.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 1000, api_response)


class EmptyOrderException(OrderServerException):
    """
    주문 요청이 비어있는 경우에 발생한다.
    "error":"Order has zero size."
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 1001, api_response)


class TooHighSlippageException(OrderServerException):
    """
    슬리피지가 너무 높은 경우 발생한다.
    "error":"Order price cannot be more than 95% away from the reference price"
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 1002, api_response)


class TooLowSlippageException(OrderServerException):
    """
    슬리피지가 너무 낮은 경우 발생한다.
    "error":"Order could not immediately match against any resting orders. asset=10107"
    """

    def __init__(self, message: str, api_response=None, status_code=400):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 1003, api_response, status_code)


class NoSuchTickerException(OrderServerException):
    """
    지원하지 않는 티커를 주문한 경우 발생한다.
    """

    def __init__(self, message: str, api_response=None, status_code=400):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 1004, api_response, status_code)


class TooSmallOrderAmountException(OrderServerException):
    """
    주문하는 금액이 10USDC 미만인 경우에 발생한다.
    """

    def __init__(self, message: str, api_response=None, status_code=400):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 1005, api_response, status_code)


class InsufficientMarginException(OrderServerException):
    """
    마진이 부족한 경우 발생한다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 1006, api_response)


class BuilderFeeNotApprovedException(OrderServerException):
    """
    Builder fee가 승인되지 않은 경우 발생한다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 1007, api_response)


class RecudeOnlyException(OrderServerException):
    """
    포지션을 닫을 때 자신이 보유한 포지션보다 더 많이 닫으려고 하기 떄문에 이에 있어서 예외가 발생함.
    reduce=True이기에 발생함
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 1008, api_response)


class TooManyCumulativeOrdersException(OrderServerException):
    """
    너무 많은 누적 주문이 발생한 경우 발생한다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 1009, api_response)


class TooManySizeException(OrderServerException):
    """
    너무 큰 금액을 요청했을 시에 예외가 발생한다.
    "error":"Order size cannot be larger than half of total supply."
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 1010, api_response)


class InsufficientSpotBalanceException(OrderServerException):
    """
    Spot 잔고가 부족할 경우 발생하는 예외
    """

    def __init__(self, message: str, api_response=None, status_code=400):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 1011, api_response, status_code)


class InvalidNonceException(OrderServerException):
    """
    주문 요청의 nonce가 유효하지 않은 경우 발생한다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 1012, api_response)


class NoSuchPositionException(OrderServerException):
    """
    요청한 포지션이 존재하지 않는 경우 발생한다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 1013, api_response)


class InsufficientUsdcException(OrderServerException):
    """
    USDC 잔액이 부족할 경우 발생한다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 1014, api_response)


class UnsupportedDeltaNeutralSymbolError(OrderServerException):
    """
    지원되지 않는 Delta-Neutral 심볼인 경우 발생한다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 1015, api_response)
