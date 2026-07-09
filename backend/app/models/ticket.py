from sqlalchemy import Column, String
from app.db.base import Base


class TicketModel(Base):
    """
    工单表，字段对应 schemas/ticket.py 里的 TicketInfo。
    """
    __tablename__ = "tickets"
    ticket_no = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    status = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    assignee = Column(String, nullable=False)
