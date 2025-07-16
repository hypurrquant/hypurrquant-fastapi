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


class AccountServerException(BaseOrderException):
    pass


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


class PnlServerExcpetion(BaseOrderException):  # 4000번대 에러
    pass


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


class StrategyServerException(BaseOrderException):  # 7000번대 에러

    pass


class InvalidFilterException(StrategyServerException):
    """ """

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 7000, api_response)


class DataException(BaseOrderException):
    pass


class MarketDataException(DataException):

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 9000, api_response)


class CandleDataException(DataException):

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 9001, api_response)


class AllMidsException(DataException):

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 9002, api_response)


class PerpMetaException(DataException):

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 9003, api_response)


class PerpMarketDataException(DataException):

    def __init__(self, message: str, api_response=None):
        """
        Args:
            message (str): Error message from APIResponse.
            code (int): Error code.
            api_response (Optional[Any]): The APIResponse object.
        """
        super().__init__(message, 9004, api_response)


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
