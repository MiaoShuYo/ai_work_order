from langchain_core.tools import tool
from app.db.session import SessionLocal
from app.models.ticket import TicketModel


@tool
def query_ticket(ticket_no: str) -> dict:
    """
    根据工单号查询工单的标题、处理状态、优先级和负责人，工单号是形如 T20260701001 的字符串，通常出现在用户之前提交工单时收到的回执里，不要和订单号或者用户 ID 混淆
    """
    db=SessionLocal()
    try:
        ticket = db.query(TicketModel).filter(
            TicketModel.ticket_no == ticket_no).first()
        if ticket is None:
            return {"error": f"未找到工单 {ticket_no}，请确认工单号是否正确。"}
        return {
            "ticket_no": ticket.ticket_no,
            "title": ticket.title,
            "status": ticket.status,
            "priority": ticket.priority,
            "assignee": ticket.assignee,
        }
    finally:
        db.close()
