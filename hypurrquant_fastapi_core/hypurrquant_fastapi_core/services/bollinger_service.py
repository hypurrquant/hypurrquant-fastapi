from hypurrquant_fastapi_core.singleton import singleton
from hypurrquant_fastapi_core.logging_config import configure_logging
from hypurrquant_fastapi_core.services.candle_service import CandleService
import pandas as pd

logger = configure_logging(__file__)


@singleton
class BollingerBandService:
    def __init__(self):
        self.candle_service = CandleService()

    async def compute_bollinger(self, coin, interval, window: int = 20) -> pd.DataFrame:
        df = await self.candle_service.fetch_candles(coin, interval)
        df = df.copy()
        df["MA"] = df["close"].rolling(window).mean()
        df["STD"] = df["close"].rolling(window).std(ddof=0)
        df["Upper"] = df["MA"] + 2 * df["STD"]
        df["Middle"] = df["MA"]  # 중간 밴드 추가
        df["Lower"] = df["MA"] - 2 * df["STD"]
        return df

    async def get_latest_band(self, df: pd.DataFrame, window: int = 20) -> tuple:
        df_bb = self.compute_bollinger(df, window)
        latest_row = df_bb.iloc[-1]
        return (
            latest_row["Upper"],
            latest_row["Lower"],
        )
