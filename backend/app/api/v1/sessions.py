import json
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.chat_message import ChatMessageModel
from app.models.chat_session import ChatSessionModel
from app.repositories.session_repository import SessionRepository
from app.schemas.session import SessionInfo, SessionMessageItem

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


def _to_session_info(session: ChatSessionModel) -> SessionInfo:
    return SessionInfo(
        session_id=session.session_id,
        thread_id=session.thread_id,
        title=session.title,
        ticket_no=session.ticket_no,
        created_at=session.created_at,
        updated_at=session.updated_at
    )


def _to_message_item(message: ChatMessageModel) -> SessionMessageItem:
    """
    ORM 消息行转响应结构。extra 是 JSON 文本，这里解开后平铺，用户消息没有 extra，所有附属字段走默认值。
    """
    extra: dict[str, Any] = {}
    if message.extra:
        try:
            extra = json.loads(message.extra)
        except json.JSONDecodeError:
            extra = {}
    return SessionMessageItem(
        role=message.role,  # type: ignore[arg-type]
        content=message.content,
        intent=extra.get("intent"),
        confidence=extra.get("confidence"),
        need_human=extra.get("need_human"),
        suggested_actions=extra.get("suggested_actions", []),
        tool_calls=extra.get("tool_calls", []),
        sources=extra.get("sources", []),
        task_intent=extra.get("task_intent"),
        created_at=message.created_at
    )


@router.post("", response_model=SessionInfo)
def create_session(db: Session = Depends(get_db)) -> SessionInfo:
    """
    创建一个新会话，返回会话概要。
    """
    session = SessionRepository(db).create_session()
    return _to_session_info(session)


@router.get("", response_model=list[SessionInfo])
def list_sessions(db: Session = Depends(get_db)) -> list[SessionInfo]:
    """
    列出所有会话概要，按最近活跃时间倒序。
    """
    return [_to_session_info(session) for session in SessionRepository(db).list_sessions()]


@router.get("/{session_id}/messages", response_model=list[SessionMessageItem])
def list_session_messages(session_id: str, db: Session = Depends(get_db)) -> list[SessionMessageItem]:
    """
    列出指定会话的所有消息，按创建时间升序。
    """
    repository = SessionRepository(db)
    if repository.get_session(session_id) is None:
        raise HTTPException(status_code=404, detail=f"会话 {session_id} 不存在")
    return [_to_message_item(message) for message in repository.list_messages(session_id)]


@router.delete("/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """
    删除指定会话及其所有消息。
    """
    repository = SessionRepository(db)
    if repository.get_session(session_id) is None:
        raise HTTPException(status_code=404, detail=f"会话 {session_id} 不存在")
    repository.delete_session(session_id)
    return {"status": "deleted", "session_id": session_id}
