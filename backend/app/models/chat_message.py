from sqlalchemy import Column, Integer, String, Text, UniqueConstraint
from app.db.base import Base


class ChatMessageModel(Base):
    """
    消息表，一行是会话里的一句发言。
    seq_no 在同一 session 内从 1 连续递增，恢复历史和记忆裁剪都按它排序。
    extra 存 AI 消息的附属数据（意图、工具调用、引用来源），整存整取，用 JSON 文本。
    """

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False, index=True)
    thread_id = Column(String, nullable=False, index=True)
    seq_no = Column(Integer, nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    extra = Column(Text, nullable=True)
    created_at = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("session_id", "seq_no",
                         name="uq_chat_messages_session_seq"),
    )
