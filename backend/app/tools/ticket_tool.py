from langchain_core.tools import tool
from app.schemas.ticket import TicketInfo

# 和 order_tool.py 一样先用内存字典模拟工单系统，真是项目里这里会换成调用工单中台的接口
