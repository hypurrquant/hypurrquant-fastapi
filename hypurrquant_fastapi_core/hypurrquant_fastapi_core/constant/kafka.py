from enum import Enum
from hypurrquant_fastapi_core.constant.projects import PROJECT_NAME, Service


class AccountKafkaTopic(Enum):
    DELETE_ACCOUNT = f"{PROJECT_NAME}.{Service.ACCOUNT.value}.account.delete"
    REBALANCE_ACCOUNT_CHANGE = (
        f"{PROJECT_NAME}.{Service.ACCOUNT.value}.rebalance.account.change"
    )
    REBALANCE_ACCOUNT_REFRESH = (
        f"{PROJECT_NAME}.{Service.ACCOUNT.value}.rebalance.account.refresh"
    )
    SPOT_BALANCE_REFRESH = (
        f"{PROJECT_NAME}.{Service.ACCOUNT.value}.spot.balance.refresh"
    )


class DataKafkaTopic(Enum):
    SPOT_MARKET_DATA_MID_PRICE = (
        f"{PROJECT_NAME}.{Service.DATA.value}.spotMarket.midPrice"
    )


class RebalanceKafkaTopic(Enum):
    REBLANACE_ACCOUNT_DELETE = (
        f"{PROJECT_NAME}.{Service.REBALANCE.value}.account.delete"
    )
    REBALANCE_ACCOUNT_REFRESH = (
        f"{PROJECT_NAME}.{Service.REBALANCE.value}.account.refresh"
    )
