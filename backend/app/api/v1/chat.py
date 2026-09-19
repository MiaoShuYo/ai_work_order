import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.agents.llm_client import stream_chat
from app.db.session import get_db
from app.repositories.session_repository import SessionRepository
from app.schemas.chat import ChatRequest

router = APIRouter()


async def _to_sse(messages: list[dict[str, str]]):
    """
    把 stream_chat 产出的事件字典逐个格式化成 SSE 要求的 event/data 文本块。
    """
    async for event in stream_chat(messages):
        event_type = event["type"]
        yield f"event: {event_type}\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"


@router.post("/chat")
async def send_message(
    request: ChatRequest, db: Session = Depends(get_db)
) -> StreamingResponse:
    # 会话不存在时在 SSE 响应头发送之前直接 404，前端能拿到标准 JSON 错误体
    if SessionRepository(db).get_session(request.session_id) is None:
        raise HTTPException(
            status_code=404, detail=f"会话 {request.session_id} 不存在")
    return StreamingResponse(
        _to_sse(request.session_id, request.message),
        media_type="text/event-stream"
    )
