from pydantic import BaseModel, Field
from typing import Optional, Union, List


class MarketData(BaseModel):
    prevDayPx: float
    dayNtlVlm: float
    markPx: float
    midPx: float
    circulatingSupply: float
    coin: str  # @108
    totalSupply: float
    dayBaseVlm: float
    tokens: Union[int, List[int]]
    name: str  # @108
    index_x: int
    isCanonical_x: bool
    token: int
    Tname: str  # CHEF -> ticker
    szDecimals: int
    weiDecimals: int
    index_y: int
    tokenId: str
    isCanonical_y: bool
    evmContract: Optional[str] = None
    fullName: Optional[str] = None  # full name은 있을 수도 있고 없을 수도 있음.
    MarketCap: float
    change_24h: float
    change_24h_pct: float
    sector: Optional[str] = None

    def __init__(self, **kwargs):
        test_set = set()
        try:
            if "24hchange" in kwargs:
                kwargs["change_24h"] = kwargs.pop("24hchange")
            elif "change_24h" in kwargs:
                kwargs["change_24h"] = kwargs.pop("change_24h")

            if "24hchange_pct" in kwargs:
                kwargs["change_24h_pct"] = kwargs.pop("24hchange_pct")
            elif "change_24h_pct" in kwargs:
                kwargs["change_24h_pct"] = kwargs.pop("change_24h_pct")

            super().__init__(**kwargs)
        except KeyError:
            print("MarketData._init__ KeyError")
