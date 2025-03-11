from enum import Enum
from hypurrquant_fastapi_core.constant.projects import PROJECT_NAME, Service
import os

PROFILE = os.getenv("PROFILE", "prod")


class AccountKafkaTopic(Enum):
    DELETE_ACCOUNT = f"{PROJECT_NAME}_{Service.ACCOUNT.value}_account_delete"
    REBALANCE_ACCOUNT_CHANGE = (
        f"{PROJECT_NAME}_{Service.ACCOUNT.value}_rebalance_account_change"
    )
    REBALANCE_ACCOUNT_REFRESH = (
        f"{PROJECT_NAME}_{Service.ACCOUNT.value}_rebalance_account_refresh"
    )
    SPOT_BALANCE_REFRESH = (
        f"{PROJECT_NAME}_{Service.ACCOUNT.value}_spot_balance_refresh"
    )


class DataKafkaTopic(Enum):
    SPOT_MARKET_DATA_MID_PRICE = (
        f"{PROJECT_NAME}_{Service.DATA.value}_spotMarket_midPrice"
    )


class RebalanceKafkaTopic(Enum):
    REBLANACE_ACCOUNT_DELETE = (
        f"{PROJECT_NAME}_{Service.REBALANCE.value}_account_delete"
    )
    REBALANCE_ACCOUNT_REFRESH = (
        f"{PROJECT_NAME}_{Service.REBALANCE.value}_account_refresh"
    )


def get_topic(default_topic: str) -> str:
    """
    env_var_name에 해당하는 환경 변수 값이 존재하면 그 값을 사용하고,
    그렇지 않으면 default_topic을 반환합니다_
    """

    if PROFILE == "prod":
        tmp = os.getenv(default_topic)
        if not tmp:
            raise ValueError(f"환경 변수 {default_topic}이 존재하지 않습니다_")
        return tmp
    else:
        return default_topic
