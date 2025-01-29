from typing import List, Union, Optional
from pydantic import BaseModel


# Define response formats
class FilledOrder(BaseModel):
    totalSz: str
    avgPx: str
    oid: int


class ErrorStatus(BaseModel):
    error: Optional[str] = None


class OrderStatus(BaseModel):
    filled: Optional[FilledOrder] = None


class OrderResponseData(BaseModel):
    statuses: List[Union[OrderStatus, ErrorStatus]]  # str이면 에러


class OrderResponse(BaseModel):
    type: str
    data: OrderResponseData


class OrderAPIResponse(BaseModel):
    status: str
    response: Union[str, OrderResponse]  # 게좌 관련 에러에서는 str
