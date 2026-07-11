from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.base import Base


class DocumentModel(Base):
    """
    文档表，file_path 存的是原始文件在本地磁盘上的路径，summary 是解析出来的文本摘要，
    status 用普通字符串存储，取值范围（处理中、已完成、失败）由业务代码在写入时保证，
    数据库层面不做约束，这一点和 schemas/document.py 里用 Literal 收紧取值范围的做法分工不同。
    """
    __tablename__ = "documents"
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="处理中")
    summary = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    chunk_count = Column(Integer, nullable=False, default=0)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
