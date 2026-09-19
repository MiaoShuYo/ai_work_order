from sqlalchemy import Column, String
from app.db.base import Base


class ChatSessionModel(Base):
    """
    会话表，一行对应左侧会话列表里的一段对话。
    session_id 是会话资源的主键，thread_id 是这段对话在短期记忆层的线程编号，
    两者创建时各自生成，当前版本固定一一对应。
    """

    __tablename__ = "chat_sessions"

    session_id = Column(String, primary_key=True)
    thread_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False, default="新会话")
    ticket_no = Column(String, nullable=True)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)
    