import os

# 비동기용
import redis.asyncio as aioredis
import redis as sync_redis
import os

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

PROFILE = os.getenv("PROFILE", "prod")

common_kwargs = {"host": REDIS_HOST, "port": REDIS_PORT, "decode_responses": True}

if PROFILE == "prod":
    common_kwargs["ssl"] = True

redis_client = aioredis.Redis(**common_kwargs)
redis_client_sync = sync_redis.Redis(**common_kwargs)
