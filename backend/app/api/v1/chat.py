from fastapi import APIRouter,HTTPException
from app.agents.llm_client import call_llm
from app.schemas.chat import ChatRequest,ChatResponse

router = APIRouter()

@router.post("/chat",response_model=ChatResponse)
async def send_message(request:ChatRequest)->ChatResponse:
    try:
        reply = await call_llm([message.model_dump() for message in request.messages])
    except Exception as exc:
        # 模型调用失败的原因可能是网络问题、密钥失效或者对方服务限流，这里统一转成 502 而不是异常直接冒泡成 500，方便前端区分"我们的接口挂了" 和 "上有模型服务不可用" 这两种不同的错误场景。
        raise HTTPException(status_code=502,detail="调用大模型服务失败") from exc
    return ChatResponse(reply=reply)