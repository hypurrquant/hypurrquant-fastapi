import os

from hypurrquant_fastapi_core.messaging.client import *
from hypurrquant_fastapi_core.logging_config import configure_logging

PROFILE = os.getenv("PROFILE", "prod")

logger = configure_logging(__name__)


def get_producer() -> AsyncMessagingProducer:
    if PROFILE == "prod":
        region_name = os.getenv("REGION_NAME")
        if not region_name:
            raise ValueError("환경 변수 REGION_NAME이 존재하지 않습니다.")
        logger.info(f"Creating SQS producer for region: {region_name}")
        return SQSMessagingProducer(
            region_name,
        )
    else:
        host = os.getenv("KAFKA_BOOTSTRAP_SERVER_HOST")
        port = os.getenv("KAFKA_BOOTSTRAP_SERVER_PORT")

        if not host or not port:
            raise ValueError(
                "환경 변수 KAFKA_BOOTSTRAP_SERVER_HOST 또는 KAFKA_BOOTSTRAP_SERVER_PORT가 존재하지않습니다."
            )

        return KafkaMessagingProducer(f"{host}:{port}")


def get_consumer(destination: str) -> AsyncMessagingConsumer:
    if PROFILE == "prod":
        region_name = os.getenv("REGION_NAME")
        if not region_name:
            raise ValueError("환경 변수 REGION_NAME이 존재하지 않습니다.")

        return SQSMessagingConsumer(
            destination,
            region_name,
        )
    else:
        host = os.getenv("KAFKA_BOOTSTRAP_SERVER_HOST")
        port = os.getenv("KAFKA_BOOTSTRAP_SERVER_PORT")

        if not host or not port:
            raise ValueError(
                "환경 변수 KAFKA_BOOTSTRAP_SERVER_HOST 또는 KAFKA_BOOTSTRAP_SERVER_PORT가 존재하지않습니다."
            )

        return KafkaMessagingConsumer(f"{host}:{port}", destination)
