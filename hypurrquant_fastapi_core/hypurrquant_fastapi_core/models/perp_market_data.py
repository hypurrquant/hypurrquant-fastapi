from pydantic import BaseModel, Field
from typing import List


class MarketData(BaseModel):
    szDecimals: int = Field(..., description="소수점 자릿수")
    name: str = Field(..., description="자산명 (예: BTC)")
    maxLeverage: int = Field(..., description="최대 레버리지 배율")

    funding: float = Field(..., description="펀딩 비율 (Funding Rate)")
    openInterest: float = Field(..., description="미결제약정 (Open Interest)")
    prevDayPx: float = Field(..., description="전일 종가 (Previous Day Price)")
    dayNtlVlm: float = Field(..., description="일일 명목 거래량 (Day Notional Volume)")
    premium: float = Field(..., description="프리미엄 (Premium)")
    oraclePx: float = Field(..., description="오라클 가격 (Oracle Price)")
    markPx: float = Field(..., description="마크 가격 (Mark Price)")
    midPx: float = Field(..., description="중간 가격 (Mid Price)")
    impactPxs: List[float] = Field(..., description="충격 가격 리스트 (Impact Prices)")
    dayBaseVlm: float = Field(..., description="일일 기초 거래량 (Day Base Volume)")

    class Config:
        json_schema_extra = {
            "example": {
                "szDecimals": 5,
                "name": "BTC",
                "maxLeverage": 50,
                "funding": 0.0000125,
                "openInterest": 10318.78506,
                "prevDayPx": 97189.0,
                "dayNtlVlm": 2004646527.47062087,
                "premium": -0.00003072,
                "oraclePx": 97644.0,
                "markPx": 97640.0,
                "midPx": 97640.5,
                "impactPxs": [97640.0, 97641.0],
                "dayBaseVlm": 20815.75431,
            }
        }
