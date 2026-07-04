from fastapi import APIRouter,HTTPException
from app.agents.llm_client import call_llm
from app.schemas.chat import ChatRequest,ChatResponse

router = APIRouter()

@router.post("/chat",response_model=ChatResponse)
async def send_message(request:ChatRequest)->ChatResponse:
    try:
        return await call_llm([message.model_dump() for message in request.messages])
    except Exception as exc:
        # 除了昨天已有的网络、密钥、限流这些原因，结构化输出还可能因为模型没有按 schema 生成合法 JSON 而抛出校验错误，这里统一按 502 处理，后续如果要单独区分"解析失败"和"上游服务不可用"，可以在这里拆分异常类型。
        raise HTTPException(status_code=502,detail="调用大模型服务失败") from exc