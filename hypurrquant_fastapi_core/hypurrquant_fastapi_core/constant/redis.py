from hypurrquant_fastapi_core.constant.projects import PROJECT_NAME, SERVICES

ACCOUNT_REDIS_KEY = {
    "REFRESH_LOCK": f"{PROJECT_NAME}:{SERVICES['account']}:refresh_lock:{{public_key}}",
    "BALANCE": f"{PROJECT_NAME}:{SERVICES['account']}:balance:{{ticker}}",
}

DATA_REDIS_KEY = {
    "ALL_MIDS": f"{PROJECT_NAME}:{SERVICES['data']}:all_mids",
    "PERP_CANDLE": f"{PROJECT_NAME}:{SERVICES['data']}:perp_candle",
    "PERP_MOMENTUM": f"{PROJECT_NAME}:{SERVICES['data']}:perp_momentum",
    "PERP_META": f"{PROJECT_NAME}:{SERVICES['data']}:perp_meta",
    "PERP_MARKET_DATA": f"{PROJECT_NAME}:{SERVICES['data']}:perp_market_data",
    "CANDLE": f"{PROJECT_NAME}:{SERVICES['data']}:candle",
    "MOMENTUM": f"{PROJECT_NAME}:{SERVICES['data']}:momentum",
    "MARKET_DATA": f"{PROJECT_NAME}:{SERVICES['data']}:market_data",
}
