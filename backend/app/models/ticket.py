from sqlalchemy import Column, String
from app.db.base import Base


class TicketModel(Base):
    """
    工单表，字段对应 schemas/ticket.py 里的 TicketInfo。
    user_id 和 order_no 记录这张工单涉及的用户与订单，方便客服在处理工单时
    顺着关联去查用户资料、订单状态、支付流水和物流轨迹。两个字段可空，
    兼容"还没核实到关联对象"的工单。
    """
    __tablename__ = "tickets"
    ticket_no = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    status = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    assignee = Column(String, nullable=False)
    user_id = Column(String, nullable=True)
    order_no = Column(String, nullable=True)
