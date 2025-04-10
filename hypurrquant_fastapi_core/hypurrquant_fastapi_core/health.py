import asyncio
import threading
from fastapi import APIRouter, HTTPException
from hypurrquant_fastapi_core.logging_config import configure_logging

logger = configure_logging(__name__)
health_router = APIRouter()

is_healthy = True  # 기본 서버 상태는 정상
lock = threading.Lock()  # 상태 변경 시 동시성을 보장하기 위한 Lock


# 상태를 비정상으로 변경하는 함수 (이미 unhealthy인 경우 무시)
async def set_unhealthy(duration: int):
    global is_healthy
    with lock:
        if not is_healthy:
            logger.info("set_unhealthy 호출은 이미 unhealthy 상태이므로 무시합니다.")
            return
        is_healthy = False

    logger.error(
        "hyperliquid의 exchange 거래소 객체 생성 중 예외가 발생했습니다. 아마 api limit을 초과했을 것입니다."
    )
    await asyncio.sleep(duration)
    with lock:
        is_healthy = True


# set_unhealthy를 호출하는 쪽에서는 백그라운드 태스크로 생성
def trigger_unhealthy(duration: int):
    # await 없이 create_task로 백그라운드에서 실행
    asyncio.create_task(set_unhealthy(duration))


@health_router.get("/health")
async def health_check():
    return {"status": "healthy"}


@health_router.get("/health/lb")
async def health_check_lb():
    with lock:
        if not is_healthy:
            raise HTTPException(status_code=503, detail="Service Unavailable")
    return {"status": "healthy"}
