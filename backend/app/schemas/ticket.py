from typing import Literal
from pydantic import BaseModel, Field


class TicketInfo(BaseModel):
    """
    工单信息，字段覆盖客服判断处理进度和优先级最常用到的几项
    """
    ticket_no: str = Field(description="工单号")
    title: str = Field(description="工单标题，概括用户诉求")
    status: Literal["待处理", "处理中", "已解决", "已关闭"] = Field(description="工单当前处理状态")
    priority: Literal["低", "中", "高", "紧急"] = Field(description="工单优先级")
    assignee: str = Field(description="当前负责处理的客服姓名，未分配时为“未分配”")
