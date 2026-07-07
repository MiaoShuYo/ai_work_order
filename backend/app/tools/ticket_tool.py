from langchain_core.tools import tool
from app.schemas.ticket import TicketInfo

# 和 order_tool.py 一样先用内存字典模拟工单系统，真是项目里这里会换成调用工单中台的接口
_MOCK_TICKETS: dict[str, TicketInfo] = {
    "T20260701001": TicketInfo(
        ticket_no="T20260701001",
        title="订单发货延迟投诉",
        status="处理中",
        priority="高",
        assignee="王芳",
    ),
    "T20260702002": TicketInfo(
        ticket_no="T20260702002",
        title="账号无法登录",
        status="待处理",
        priority="紧急",
        assignee="未分配",
    ),
}


@tool
def query_ticket(ticket_no: str) -> dict:
    """
    根据工单号查询工单的标题、处理状态、优先级和负责人，工单号是形如 T20260701001 的字符串，通常出现在用户之前提交工单时收到的回执里，不要和订单号或者用户 ID 混淆
    """
    ticket = _MOCK_TICKETS.get(ticket_no)
    if ticket is None:
        return {"error": f"未找到工单 {ticket_no}，请确认工单号是否正确。"}
    return ticket.model_dump()
