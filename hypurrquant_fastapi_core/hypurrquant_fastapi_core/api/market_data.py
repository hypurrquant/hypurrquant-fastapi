from hypurrquant_fastapi_core.models.market_data import MarketData
from hypurrquant_fastapi_core.singleton import singleton
from hypurrquant_fastapi_core.api.async_http import send_request
from hypurrquant_fastapi_core.logging_config import configure_logging
from hypurrquant_fastapi_core.exception import (
    NoSuchTickerException,
    MarketDataException,
)


from typing import List, Dict
import tracemalloc
import os
from dotenv import load_dotenv
import asyncio
import threading

load_dotenv()

tracemalloc.start()

logger = configure_logging(__name__)
DATA_SERVER_URL = os.getenv("BASE_URL")


@singleton
class HyqFetch:
    def __init__(self):
        self._market_datas: List[MarketData] = []
        self._coin_list = []
        self._coin_by_Tname: Dict[str, MarketData] = None
        self._Tname_by_coin: Dict[str, MarketData] = None
        self._lock = threading.RLock()  # 재진입 가능한 락

    @property
    def coin_list(self):
        with self._lock:
            if not self._coin_list:
                logger.error("Coin list is empty")
            return self._coin_list

    @property
    def coin_by_Tname(self):
        with self._lock:
            if not self._coin_by_Tname:
                logger.error("Coin by Tname is empty")
            return self._coin_by_Tname

    @property
    def Tname_by_coin(self):
        with self._lock:
            if not self._Tname_by_coin:
                logger.error("Tname by coin is empty")
            return self._Tname_by_coin

    @property
    def market_datas(self):
        with self._lock:
            if not self._market_datas:
                logger.error("Market data is empty")
                raise MarketDataException("Market data is empty")
            return self._market_datas

    def get_coin_list(self):
        return [spot_meta.coin for spot_meta in self.market_datas]

    async def _fetcg_market_data(self):
        try:
            response = await send_request("GET", f"{DATA_SERVER_URL}/data/market-data")
            return [MarketData(**data) for data in response.data]
        except:
            logger.error("Failed to fetch market data")
            raise MarketDataException("Failed to fetch market data")

    async def build_data(self):
        try:
            new_market_datas = await self._fetcg_market_data()
            new_coin_by_Tname = {data.Tname: data for data in new_market_datas}
            new_Tname_by_coin = {data.coin: data for data in new_market_datas}
            new_coin_list = [spot_meta.coin for spot_meta in new_market_datas]
            with self._lock:
                self._market_datas = new_market_datas
                self._coin_by_Tname = new_coin_by_Tname
                self._Tname_by_coin = new_Tname_by_coin
                self._coin_list = new_coin_list
        except Exception as e:
            logger.error(f"Failed to build market data: {e}")
            raise

    def filter_by_Tname(self, Tname):
        with self._lock:
            data = self.coin_by_Tname.get(Tname)
            if not data:
                error_message = f"{Tname} is not in market data"
                logger.error(error_message)
                raise NoSuchTickerException(error_message)
            return data

    def filter_by_coin(self, coin):
        with self._lock:
            data = self.Tname_by_coin.get(coin)
            if not data:
                logger.error(f"{coin} is not in market data")
                raise MarketDataException(f"{coin} is not in market data")
            return data


hyqFetch = HyqFetch()


async def periodic_task(interval):
    while True:
        try:
            await hyqFetch.build_data()
        except Exception as e:
            logger.exception(f"market data fetch failed")
        await asyncio.sleep(interval)
