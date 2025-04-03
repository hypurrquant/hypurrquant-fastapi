from pydantic import BaseModel
from typing import Any, Optional
from hypurrquant_fastapi_core.logging_config import configure_logging
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

logger = configure_logging(__name__)


# ================================
# 공통 응답 dto
# ================================
class BaseResponse(BaseModel):
    code: int
    data: Any
    error_message: Optional[str] = None
    message: Optional[str] = None


# ================================
# 성공 응답을 위한 함수
# ================================
def success_response(data: Any, message: str = None) -> JSONResponse:
    response = BaseResponse(code=200, data=data, message=message)
    encoded_content = jsonable_encoder(response.model_dump())
    return JSONResponse(status_code=200, content=encoded_content)
