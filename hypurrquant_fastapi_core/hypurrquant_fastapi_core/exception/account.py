from hypurrquant_fastapi_core.exception.base import BaseOrderException


class AccountServerException(BaseOrderException):
    pass


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


class MaxAccountsReachedException(AccountServerException):
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


class DuplicateNicknameException(AccountServerException):
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


class NoSuchAccountByProvidedNickName(AccountServerException):
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


class NoSuchAccountByProvidedTelegramId(AccountServerException):
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


class CannotDeleteAllAccounts(AccountServerException):
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


class InvalidSecretKey(AccountServerException):
    """ """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 3006, api_response)


class SendUsdcException(AccountServerException):
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


class InsufficientPerpBalanceException(AccountServerException):
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


class NoSuchAccountByProvidedPublicKey(AccountServerException):
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


class RebalanceAccountAlreadyExistsException(AccountServerException):
    """
    리밸런스 계좌가 이미 존재한다.
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 3011, api_response)


class ShouldBeTradingAcocuntException(AccountServerException):
    """
    트레이딩 계좌가 아닌 경우 발생한다.
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 3012, api_response)


class RebalanceAccountNotRegisteredException(AccountServerException):
    """
    리밸런스 계좌가 이미 존재한다.
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 3013, api_response)


class NoRebalanceDetailsException(AccountServerException):
    """
    리밸런스 계좌에 대한 상세 정보가 없다.
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 3014, api_response)


class AlreadyRegisteredAccountException(AccountServerException):
    """
    이미 등록된 계좌에 대한 예외입니다.
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 3015, api_response)


class CannotApproveBuilderFeeException(AccountServerException):
    """
    Builder fee를 승인할 수 없는 경우 발생한다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 3016, api_response)


class CannotFoundReferralCodeException(AccountServerException):
    """
    추천 코드가 존재하지 않는 경우 발생한다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 3017, api_response)


class CannotAddReferralException(AccountServerException):
    """
    추천인 추가에 실패한 경우 발생한다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 3018, api_response)


class NoSuchReferralCodeException(AccountServerException):
    """
    추천 코드가 존재하지 않는 경우 발생한다.
    """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 3019, api_response)


class UsdTransferSmmllerThanFeeException(AccountServerException):
    """
    USDC 전송 금액이 수수료보다 작은 경우 발생한다.
    """

    def __init__(self, message: str, api_response=None, status_code=400):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 3020, api_response, status_code)


class ShouldBeDexLpVaultAccountException(AccountServerException):
    """
    AccountDetail이 DEX LP Vault 계좌가 아닌 경우 발생한다.
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 3021, api_response)


class AccountTypeNotFoundException(AccountServerException):
    """
    계좌 타입이 존재하지 않는 경우 발생한다.
    """

    def __init__(self, response: str, api_response=None):
        """
        Args:
            response (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(response, 3022, api_response)


class InsufficientBalanceException(AccountServerException):
    """
    출금하는 금액이 10USDC 미만인 경우에 발생한다.
    """

    def __init__(self, message: str, api_response=None, status_code=400):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 3100, api_response, status_code)
