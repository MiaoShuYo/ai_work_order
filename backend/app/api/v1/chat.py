import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.agents.llm_client import stream_chat
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
async def send_message(request: ChatRequest) -> StreamingResponse:
    payload = [message.model_dump() for message in request.messages]
    return StreamingResponse(_to_sse(payload), media_type="text/event-stream")
