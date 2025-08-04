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
