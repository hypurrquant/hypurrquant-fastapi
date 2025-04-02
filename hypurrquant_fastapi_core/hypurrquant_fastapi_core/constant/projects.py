from enum import Enum

PROJECT_NAME = "hypurrquant"


class Service(Enum):
    ACCOUNT = "account"
    REBALANCE = "rebalance"
    FETCH = "fetch"
    DATA = "data"
    ORDER = "order"
    STRATEGY = "strategy"
    TELEGRAM = "telegram"
    ALARM = "alarm"
    COPYTRADING = "copytrading"
