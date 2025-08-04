from hypurrquant_fastapi_core.exception.base import BaseOrderException


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
