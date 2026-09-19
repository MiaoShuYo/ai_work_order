import json
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.chat_message import ChatMessageModel
from app.models.chat_session import ChatSessionModel

_DEFAULT_TITLE = "新会话"


def _now_str() -> str:
    """
    统一的时间文本格式，全项目的时间字段都按这个格式存。
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class SessionRepository:
    """
    会话与消息的唯一读写出口，路由和流式链路都通过它操作两张表，避免查询散落在业务代码里。
    """

    def __init__(self, db: Session):
        self.db = db

    def create_session(self) -> ChatSessionModel:
        now = _now_str()
        session = ChatSessionModel(
            session_id=uuid.uuid4().hex,
            thread_id=uuid.uuid4().hex,
            title=_DEFAULT_TITLE,
            ticket_no=None,
            created_at=now,
            updated_at=now,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: str) -> Optional[ChatSessionModel]:
        return (
            self.db.query(ChatSessionModel)
            .filter(ChatSessionModel.session_id == session_id)
            .first()
        )

    def list_sessions(self) -> list[ChatSessionModel]:
        """
        会话列表按最近活跃时间倒序，刚聊过的会话排在最上面。
        """
        return (
            self.db.query(ChatSessionModel)
            .order_by(ChatSessionModel.updated_at.desc())
            .all()
        )

    def delete_session(self, session_id: str) -> None:
        # 逻辑外键没有级联，必须先删消息再删会话，否则会留下孤儿消息行
        self.db.query(ChatMessageModel).filter(
            ChatMessageModel.session_id == session_id).delete(synchronize_session=False)
        self.db.query(ChatSessionModel).filter(
            ChatSessionModel.session_id == session_id).delete(synchronize_session=False)
        self.db.commit()

    def touch(self, session_id: str) -> None:
        """
        刷新最近活跃时间，每轮对话开头和结束各调一次。
        """
        session = self.get_session(session_id)
        if session is not None:
            session.updated_at = _now_str()
            self.db.commit()

    def update_title(self, session_id: str, title: str) -> None:
        session = self.get_session(session_id)
        if session is not None:
            session.title = title
            self.db.commit()

    def link_ticket(self, session_id: str, ticket_no: str) -> None:
        session = self.get_session(session_id)
        if session is not None:
            session.ticket_no = ticket_no
            self.db.commit()

    def append_message(
            self,
            session_id: str,
            thread_id: str,
            role: str,
            content: str,
            extra: Optional[dict] = None,
    ) -> ChatMessageModel:
        """
        追加一条消息，seq_no 取当前会话最大值加一。
        唯一约束 uq_chat_messages_session_seq 负责并发场景的兜底。
        """
        current_max = (
            self.db.query(func.coalesce(func.max(ChatMessageModel.seq_no), 0))
            .filter(ChatMessageModel.session_id == session_id)
            .scalar()
        )
        message = ChatMessageModel(
            session_id=session_id,
            thread_id=thread_id,
            seq_no=current_max+1,
            role=role,
            content=content,
            extra=json.dumps(extra, ensure_ascii=False) if extra else None,
            created_at=_now_str()
        )
        self.db.add(message)
        self.db.commit()
        return message

    def list_messages(self, session_id: str) -> list[ChatMessageModel]:
        """会话恢复用，返回全量消息，时间正序。"""
        return (
            self.db.query(ChatMessageModel)
            .filter(ChatMessageModel.session_id == session_id)
            .order_by(ChatMessageModel.seq_no.asc())
            .all()
        )

    def list_context_messages(self, thread_id: str, limit: int) -> list[ChatMessageModel]:
        """
        模型上下文用，只取最近 limit 条。倒序取完再反转，保证喂给模型的消息仍然是时间正序，顺序乱了对话角色会对不上。
        """
        rows = (
            self.db.query(ChatMessageModel)
            .filter(ChatMessageModel.thread_id == thread_id)
            .order_by(ChatMessageModel.seq_no.desc())
            .limit(limit)
            .all()
        )
        return list(reversed(rows))
