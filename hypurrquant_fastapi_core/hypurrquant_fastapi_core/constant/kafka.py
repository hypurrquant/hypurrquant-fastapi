from enum import Enum
from hypurrquant_fastapi_core.constant.projects import PROJECT_NAME, SERVICES


class AccountKafkaTopic(Enum):
    DELETE_ACCOUNT = f"{PROJECT_NAME}.{SERVICES['account']}.account.delete"
    REBALANCE_ACCOUNT_CHANGE = (
        f"{PROJECT_NAME}.{SERVICES['account']}.rebalance.account.change"
    )
    REBALANCE_ACCOUNT_REFRESH = (
        f"{PROJECT_NAME}.{SERVICES['account']}.rebalance.account.refresh"
    )
    SPOT_BALANCE_REFRESH = f"{PROJECT_NAME}.{SERVICES['account']}.spot.balance.refresh"


class DataKafkaTopic(Enum):
    SPOT_MARKET_DATA_MID_PRICE = (
        f"{PROJECT_NAME}.{SERVICES['data']}.spotMarket.midPrice"
    )
