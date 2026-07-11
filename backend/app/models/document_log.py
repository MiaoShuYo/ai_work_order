from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.db.base import Base


class DocumentLogModel(Base):
    """
    文档处理日志，每一次状态推进都追加一条记录，不做更新和去重，
    用来在前端完整回放某份文档从上传到可检索（或失败）经历的每一步
    """

    __tablename__ = "document_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    step = Column(String, nullable=False)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
