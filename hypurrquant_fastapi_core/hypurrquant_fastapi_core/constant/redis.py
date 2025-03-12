from hypurrquant_fastapi_core.constant.projects import PROJECT_NAME, Service

from enum import Enum


class AccountRedisKey(Enum):
    REFRESH_LOCK = f"{PROJECT_NAME}:{Service.ACCOUNT.value}:refresh_lock:{{public_key}}"
    BALANCE = f"{PROJECT_NAME}:{Service.ACCOUNT.value}:balance:{{ticker}}"


class DataRedisKey(Enum):
    ALL_MIDS = f"{PROJECT_NAME}:{Service.DATA.value}:all_mids"
    ALL_MIDS_COUNT = f"{PROJECT_NAME}:all_mids_count"
    PERP_CANDLE = f"{PROJECT_NAME}:{Service.DATA.value}:perp_candle"
    PERP_MOMENTUM = f"{PROJECT_NAME}:{Service.DATA.value}:perp_momentum"
    PERP_META = f"{PROJECT_NAME}:{Service.DATA.value}:perp_meta"
    PERP_MARKET_DATA = f"{PROJECT_NAME}:{Service.DATA.value}:perp_market_data"
    CANDLE = f"{PROJECT_NAME}:{Service.DATA.value}:candle"
    MOMENTUM = f"{PROJECT_NAME}:{Service.DATA.value}:momentum"
    MARKET_DATA = f"{PROJECT_NAME}:{Service.DATA.value}:market_data"


class RebalanceRedisKey(Enum):
    PNL_PER_TICKER = f"{PROJECT_NAME}:{Service.REBALANCE.value}:pnl:{{ticker}}"
    PNL_TOTAL_PER_PUBLIC_KEY = f"{PROJECT_NAME}:{Service.REBALANCE.value}:pnl:total"
