from hypurrquant_fastapi_core.constant.projects import PROJECT_NAME, SERVICES

ACCOUNT_KAFKA_TOPIC = {
    "DELETE_ACCOUNT": f"{PROJECT_NAME}.{SERVICES['account']}.account.delete",
    "REBALANCE_ACCOUNT_CAHNGE": f"{PROJECT_NAME}.{SERVICES['account']}.rebalance.account.change",
    "REBALACNE_ACCOUNT_REFRESH": f"{PROJECT_NAME}.{SERVICES['account']}.rebalance.account.refresh",
    "SPOT_BALANCE_REFRESH": f"{PROJECT_NAME}.{SERVICES['account']}.spot.balance.refresh",
}

DATA_KAFKA_TOPIC = {
    "SPOT_MARKET_DATA_MID_PRICE": f"{PROJECT_NAME}.{SERVICES['data']}.spotMarket.mid_price"
}
