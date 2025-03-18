from enum import Enum
from hypurrquant_fastapi_core.constant.projects import PROJECT_NAME, Service
import os
import boto3
import botocore.exceptions
import sys

from hypurrquant_fastapi_core.logging_config import configure_logging

logger = configure_logging(__name__)


PROFILE = os.getenv("PROFILE", "prod")


class AccountKafkaTopic(Enum):
    DELETE_ACCOUNT = f"{PROJECT_NAME}_{Service.ACCOUNT.value}_account_delete"
    REBALANCE_ACCOUNT_CHANGE = (
        f"{PROJECT_NAME}_{Service.ACCOUNT.value}_rebalance_account_change"
    )
    REBALANCE_ACCOUNT_REFRESH = (
        f"{PROJECT_NAME}_{Service.ACCOUNT.value}_rebalance_account_refresh"
    )
    SPOT_BALANCE_REFRESH = (
        f"{PROJECT_NAME}_{Service.ACCOUNT.value}_spot_balance_refresh"
    )


class DataKafkaTopic(Enum):
    SPOT_MARKET_DATA_MID_PRICE = (
        f"{PROJECT_NAME}_{Service.DATA.value}_spotMarket_midPrice"
    )


class RebalanceKafkaTopic(Enum):
    REBLANACE_ACCOUNT_DELETE = (
        f"{PROJECT_NAME}_{Service.REBALANCE.value}_account_delete"
    )
    REBALANCE_ACCOUNT_REFRESH = (
        f"{PROJECT_NAME}_{Service.REBALANCE.value}_account_refresh"
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
    client = session.client("sqs", region_name="us-west-2")

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
