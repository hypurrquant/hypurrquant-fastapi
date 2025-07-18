from enum import Enum
from hyperliquid.utils.constants import MAINNET_API_URL
import os

PROJECT_NAME = "hypurrquant"

HYPERLIQUID_API_URL = os.environ.get("HYPERLIQUID_API_URL", MAINNET_API_URL)


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
    DEX = "dex"
