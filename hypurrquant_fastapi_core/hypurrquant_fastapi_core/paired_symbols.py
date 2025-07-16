from enum import Enum
from typing import Dict


# 1) 마켓 타입 열거형 정의
class MarketType(Enum):
    PERP = "perp"
    SPOT = "spot"


# 2) 각 심볼의 설정 구조
class SymbolConfig:
    def __init__(self, display: str, internal: Dict[MarketType, str]):
        self.display = display
        self.internal = internal


# 3) 전체 심볼 매핑 테이블
symbol_table: Dict[str, SymbolConfig] = {
    "BTC": SymbolConfig(
        display="BTC",
        internal={
            MarketType.PERP: "BTC",  # perp 시장용 내부 심볼
            MarketType.SPOT: "UBTC",  # spot 시장용 내부 심볼
        },
    ),
    "ETH": SymbolConfig(
        display="ETH",
        internal={
            MarketType.PERP: "ETH",
            MarketType.SPOT: "UETH",
        },
    ),
    "SOL": SymbolConfig(
        display="SOL",
        internal={
            MarketType.PERP: "SOL",
            MarketType.SPOT: "USOL",
        },
    ),
    "HYPE": SymbolConfig(
        display="HYPE",
        internal={
            MarketType.PERP: "HYPE",
            MarketType.SPOT: "HYPE",
        },
    ),
}


# 4) 헬퍼 함수
def get_symbol_config(user_sym: str) -> SymbolConfig:
    cfg = symbol_table.get(user_sym)
    if not cfg:
        raise KeyError(f"Unknown symbol: {user_sym}")  # TODO 예외 정의 필요함
    return cfg
