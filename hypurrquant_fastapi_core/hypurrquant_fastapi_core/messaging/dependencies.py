import os

from hypurrquant_fastapi_core.messaging.client import *

PROFILE = os.getenv("PROFILE", "prod")


def get_producer() -> AsyncMessagingProducer:
    if PROFILE == "prod":
        region_name = os.getenv("REGION_NAME")
        if not region_name:
            raise ValueError("환경 변수 REGION_NAME이 존재하지 않습니다.")

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

        return KafkaMessaingProducer(f"{host}:{port}")


def get_consumer(destination: str) -> AsyncMessagingConsumer:
    if PROFILE == "prod":
        region_name = os.getenv("REGION_NAME")
        queue_url = os.getenv("QUEUE_URL")
        if not region_name or not queue_url:
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

        return KafkaMessaingConsumer(f"{host}:{port}", destination)
