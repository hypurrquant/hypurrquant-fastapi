from hypurrquant_fastapi_core.models.perp_market_data import (
    MarketData as PerpMarketData,
)
from hypurrquant_fastapi_core.singleton import singleton
from hypurrquant_fastapi_core.logging_config import configure_logging, coroutine_logging
from hypurrquant_fastapi_core.api.async_http import send_request
from hypurrquant_fastapi_core.graceful_shutdown import GracefulShutdownMixin
from hypurrquant.api.utils import BASE_URL

from typing import Dict
import tracemalloc

tracemalloc.start()

logger = configure_logging(__name__)


@singleton
class PerpMarketDataCache(GracefulShutdownMixin):
    def __init__(self):
        super().__init__()
        self.market_datas: Dict["str", PerpMarketData] = {}

    @coroutine_logging
    async def _fetch_market_data(self):
        response = await send_request(
            "GET",
            f"{BASE_URL}/data/perp-market-data",
        )

        market_data = {}
        for key, value in response.data.items():
            market_data[key] = PerpMarketData(**value)

        return market_data

    async def _build_data(self):
        self.market_datas = await self._fetch_market_data()

    async def run_once(self):
        await perp_market_data_cache._build_data()


perp_market_data_cache = PerpMarketDataCache()
