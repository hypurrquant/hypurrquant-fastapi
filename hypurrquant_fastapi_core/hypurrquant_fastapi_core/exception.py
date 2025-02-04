from fastapi import HTTPException


class BaseOrderException(HTTPException):
    """Base class for order-related exceptions."""

    def __init__(self, message: str, code: int, api_response=None, status_code=400):
        """
        Args:
            message (str): Error message.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object or related data.
        """
        self.api_response = api_response or {}
        self.message = message
        self.code = code
        super().__init__(
            status_code,
            {"message": message, "code": code, "api_response": api_response},
        )


class InvalidSecretKeyInL1ChainException(BaseOrderException):
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


class EmptyOrderException(BaseOrderException):
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


class TooHighSlippageException(BaseOrderException):
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


class TooLowSlippageException(BaseOrderException):
    """
    슬리피지가 너무 낮은 경우 발생한다.
    "error":"Order could not immediately match against any resting orders. asset=10107" # TODO 10107은 아마 @107인듯
    """

    def __init__(self, message: str, api_response=None, status_code=400):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 1003, api_response, status_code)


class NoSuchTickerException(BaseOrderException):
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


class TooSmallOrderAmountException(BaseOrderException):
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


class MaxAccountsReachedException(BaseOrderException):
    """
    최대 계정 수는 3개까지만 가능하다.
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 3001, api_response)


class DuplicateNicknameException(BaseOrderException):
    """
    닉네임은 중복될 수 없다.
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 3002, api_response)


class NoSuchAccountByProvidedNickName(BaseOrderException):
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


class NoSuchAccountByProvidedTelegramId(BaseOrderException):
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


class CannotDeleteAllAccounts(BaseOrderException):
    """
    모든 계정을 삭제할 수 없다.
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 3005, api_response)


class InvalidSecretKey(BaseOrderException):
    """ """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 3006, api_response)


class SendUsdcException(BaseOrderException):
    """
    USDC 전송에 실패했다.
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 3007, api_response)


class InsufficientSpotBalanceException(BaseOrderException):
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
        super().__init__(message, 3008, api_response, status_code)


class InsufficientPerpBalanceException(BaseOrderException):
    """
    Perp 잔고가 부족할 경우 발생하는 예외
    """

    def __init__(self, message: str, api_response=None, status_code=400):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 3009, api_response, status_code)


class NoSuchAccountByProvidedPublicKey(BaseOrderException):
    """
    주어진 public key를 가진 계좌가 없다.
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 3010, api_response)


class InsufficientBalanceException(BaseOrderException):
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
        super().__init__(message, 3100, api_response, status_code)


class InvalidFilterException(BaseOrderException):
    """ """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 7000, api_response)


class MarketDataException(BaseException):

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 9000, api_response)


class CandleDataException(BaseException):

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 9001, api_response)


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
