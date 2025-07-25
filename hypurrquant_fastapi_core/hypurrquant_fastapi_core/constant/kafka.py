from enum import Enum
from hypurrquant_fastapi_core.constant.projects import PROJECT_NAME, Service
import os
import boto3
import botocore.exceptions
import sys

from hypurrquant_fastapi_core.logging_config import configure_logging

logger = configure_logging(__name__)


PROFILE = os.getenv("PROFILE", "prod")
REGION_NAME = os.getenv("REGION_NAME")


class AccountKafkaTopic(Enum):
    BALANCE_REFRESH = f"{PROJECT_NAME}_{Service.ACCOUNT.value}_spot_balance_refresh"  # order 서버에서 buy, sell, perp 구매하면 발행하는 이벤트


class DataKafkaTopic(Enum):
    SPOT_MARKET_DATA_MID_PRICE = f"{PROJECT_NAME}_{Service.DATA.value}_spotMarket_midPrice.fifo"  # fetch 서버에서 발행하는 이벤트
    PERPETUAL_MARKET_DATA_MID_PRICE = f"{PROJECT_NAME}_{Service.DATA.value}_perpetualMarket_midPrice.fifo"  # fetch 서버에서 발행하는 이벤트


class RebalanceKafkaTopic(Enum):
    REBLANACE_ACCOUNT_DELETE = f"{PROJECT_NAME}_{Service.REBALANCE.value}_account_delete"  # rebalance 서버에서 계좌 삭제 시 발행하는 이벤트, 지금은 redis에서 spot을 삭제하는데
    REBALANCE_ACCOUNT_REFRESH = f"{PROJECT_NAME}_{Service.REBALANCE.value}_account_refresh"  # account 서버에서 spot refresh 시 발행하는 이벤트, perp refresh 시에도 발행되게 하자.


class CopyTradingKafkaTopic(Enum):
    SUBSCRIPTION_TARGET_REGISTER = (
        f"{PROJECT_NAME}_{Service.COPYTRADING.value}_subscription_target_register.fifo"
    )
    ACCOUNT_DELETE = f"{PROJECT_NAME}_{Service.COPYTRADING.value}_account_delete"


class OrderKakfaTopic(Enum):
    PERP_OPEN = f"{PROJECT_NAME}_{Service.ORDER.value}_perp_open.fifo"
    PERP_CLOSE = f"{PROJECT_NAME}_{Service.ORDER.value}_perp_close.fifo"
    PERP_ALL_CLOSE = f"{PROJECT_NAME}_{Service.ORDER.value}_perp_closeAll.fifo"

    SPOT_BUY = f"{PROJECT_NAME}_{Service.ORDER.value}_spot_buy.fifo"
    SPOT_SELL = f"{PROJECT_NAME}_{Service.ORDER.value}_spot_sell.fifo"


class AlarmKafkaTopic(Enum):
    SEND_MESSAGE_TO_TELEGRAM = (
        f"{PROJECT_NAME}_{Service.ALARM.value}_sendMessageToTelegram.fifo"
    )


class DexKafkaTopic(Enum):
    LP_VAULT_REGISTER = f"{PROJECT_NAME}_{Service.DEX.value}_lpvault_execute.fifo"
    LP_VAULT_DELETE = f"{PROJECT_NAME}_{Service.DEX.value}_lpvault_delete.fifo"


class CommonKafkaTopic(Enum):
    DELEGATE = (
        f"{PROJECT_NAME}_common_delegate.fifo"  # delegate 서버에서 발행하는 이벤트
    )


def get_topic(default_topic: str) -> str:
    """
    env_var_name에 해당하는 환경 변수 값이 존재하면 그 값을 사용하고,
    그렇지 않으면 default_topic을 반환합니다_
    """

    if PROFILE == "prod":
        return get_sqs_queue_url(default_topic)
    else:
        return default_topic


def get_sqs_queue_url(topic: str):
    session = boto3.Session()
    client = session.client("sqs", region_name=REGION_NAME)

    try:
        response = client.get_queue_url(QueueName=topic)
    except botocore.exceptions.ClientError as err:
        if err.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue":
            print(f"Queue {topic} does not exist")
            sys.exit(1)
        else:
            raise

    queue_url = response["QueueUrl"]
    logger.info(f"topic: {topic} / Queue URL: {queue_url}")
    return queue_url
