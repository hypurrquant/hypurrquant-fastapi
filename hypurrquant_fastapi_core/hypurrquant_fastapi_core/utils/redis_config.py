import os

# 비동기용
import redis.asyncio as aioredis
import redis as sync_redis
import os

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

redis_client = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
redis_client_sync = sync_redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, decode_responses=True
)
