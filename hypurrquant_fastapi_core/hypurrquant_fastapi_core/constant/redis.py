from hypurrquant_fastapi_core.constant.projects import PROJECT_NAME, Service

from enum import Enum


class AccountRedisKey(Enum):
    REFRESH_LOCK = f"{PROJECT_NAME}:{Service.ACCOUNT.value}:refresh_lock:{{public_key}}"
    BALANCE = f"{PROJECT_NAME}:{Service.ACCOUNT.value}:balance:{{ticker}}"
    PERP_BALANCE = f"{PROJECT_NAME}:{Service.ACCOUNT.value}:perp_balance:{{ticker}}"


class DataRedisKey(Enum):
    ALL_MIDS = f"{PROJECT_NAME}:{Service.DATA.value}:all_mids"
    ALL_MIDS_COUNT = f"{PROJECT_NAME}:all_mids_count"
    PERP_ALL_MIDS_COUNT = f"{PROJECT_NAME}:perp_all_mids_count"
    PERP_CANDLE = f"{PROJECT_NAME}:{Service.DATA.value}:perp_candle"
    PERP_MOMENTUM = f"{PROJECT_NAME}:{Service.DATA.value}:perp_momentum"
    PERP_META = f"{PROJECT_NAME}:{Service.DATA.value}:perp_meta"
    PERP_MARKET_DATA = f"{PROJECT_NAME}:{Service.DATA.value}:perp_market_data"
    CANDLE = f"{PROJECT_NAME}:{Service.DATA.value}:candle"
    MOMENTUM = f"{PROJECT_NAME}:{Service.DATA.value}:momentum"
    MARKET_DATA = f"{PROJECT_NAME}:{Service.DATA.value}:market_data"

    # 실제 데이터 그대로
    RAW_SPOT_META = f"{PROJECT_NAME}:{Service.DATA.value}:raw_spot_meta"
    RAW_PERP_META = f"{PROJECT_NAME}:{Service.DATA.value}:raw_perp_meta"


class RebalanceRedisKey(Enum):
    PNL_PER_TICKER = f"{PROJECT_NAME}:{Service.REBALANCE.value}:pnl:{{ticker}}"
    PNL_PER_TICKER_PERP = (
        f"{PROJECT_NAME}:{Service.REBALANCE.value}:perp_pnl:{{ticker}}"
    )
    PNL_TOTAL_PER_PUBLIC_KEY = (
        f"{PROJECT_NAME}:{Service.REBALANCE.value}:total_pnl:{{public_key}}"
    )
    PNL_TOTAL_PER_PUBLIC_KEY_PERP = (
        f"{PROJECT_NAME}:{Service.REBALANCE.value}:perp_total_pnl:{{public_key}}"
    )


class AlarmRedisKey(Enum):
    ALARM = f"{PROJECT_NAME}:{Service.ALARM.value}:total_pnl_alarm:{{public_key}}"
    ALARM_PERP = (
        f"{PROJECT_NAME}:{Service.ALARM.value}:perp_total_pnl_alarm:{{public_key}}"
    )


class CopytradingRedisKey(Enum):
    SUBSCRIBE_HEARTBEAT = f"{PROJECT_NAME}:{Service.COPYTRADING.value}:subscription:heartbeat:{{target_public_key}}"
    SUBSCRIPTION_LOCK = f"{PROJECT_NAME}:{Service.COPYTRADING.value}:subscription:{{target_public_key}}:lock"
    ORDER_HISTORY = f"{PROJECT_NAME}:{Service.COPYTRADING.value}:subscription:order:{{target_public_key}}:{{oid}}"
    ORDER_LOCK = f"{PROJECT_NAME}:{Service.COPYTRADING.value}:subscription:order:{{target_public_key}}:{{oid}}:lock"
