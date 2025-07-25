from hypurrquant_fastapi_core.singleton import singleton
from hypurrquant_fastapi_core.constant.redis import DataRedisKey
from hypurrquant_fastapi_core.utils.redis_config import redis_client
from hypurrquant_fastapi_core.logging_config import configure_logging
from hypurrquant_fastapi_core.exception import *
import pandas as pd
import json

logger = configure_logging(__file__)


@singleton
class CandleService:
    async def fetch_candles(self, ticker: str, interval: str) -> pd.DataFrame:
        response = await redis_client.get(
            DataRedisKey.CANDLE_BY_TICKER_INTERVAL.value.format(
                ticker=ticker, interval=interval
            )
        )
        if response is None:
            raise CandleDataException(
                message=f"{ticker}의 {interval} 캔들 데이터가 없습니다."
            )

        data = json.loads(response)

        df = pd.DataFrame(data)
        df.rename(
            columns={
                "t": "time",
                "o": "open",
                "h": "high",
                "l": "low",
                "c": "close",
                "v": "volume",
            },
            inplace=True,
        )
        df["time"] = pd.to_datetime(df["time"], unit="ms")
        df.set_index("time", inplace=True)
        df = df.astype(
            {
                "open": float,
                "high": float,
                "low": float,
                "close": float,
                "volume": float,
            }
        )
        return df
