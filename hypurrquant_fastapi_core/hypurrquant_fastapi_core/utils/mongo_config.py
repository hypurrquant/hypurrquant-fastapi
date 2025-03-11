from motor.motor_asyncio import AsyncIOMotorClient
import os
from hypurrquant_fastapi_core.logging_config import configure_logging

logger = configure_logging(__name__)

# ================================
# 설정 정보 가져오기
# ================================
PROFILE = os.getenv("PROFILE", "prod")
DB_CLUSTER_ENDPOINT = os.getenv("DB_CLUSTER_ENDPOINT")
DB_PORT = os.getenv("DB_PORT", 27017)  # 기본 포트 27017
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")  # 기본 데이터베이스 이름
CERT_PATH = os.getenv("CERT_PATH")


if PROFILE == "test":
    logger.info(f"PROFILE: {PROFILE}")
    MONGO_URI = f"mongodb://{DB_USERNAME}:{DB_PASSWORD}@{DB_CLUSTER_ENDPOINT}:{DB_PORT}/{DB_NAME}?authSource=admin&replicaSet=rs0"
elif PROFILE == "virtual":
    logger.info(f"PROFILE: {PROFILE}")
    DB_NAME = "VIRTUAL"
    MONGO_URI = f"mongodb://{DB_USERNAME}:{DB_PASSWORD}@{DB_CLUSTER_ENDPOINT}:{DB_PORT}/{DB_NAME}?authSource=admin&replicaSet=rs0"
else:
    logger.info("PROFILE: prod")
    MONGO_URI = (
        f"mongodb://{DB_USERNAME}:{DB_PASSWORD}@{DB_CLUSTER_ENDPOINT}:{DB_PORT}/"
        f"?tls=true"
        f"&tlsCAFile={CERT_PATH}"
        f"&replicaSet=rs0"
        f"&readPreference=secondaryPreferred"
        f"&retryWrites=false"
    )

logger.info(f"Connecting to MongoDB: {MONGO_URI}")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
