from typing import Literal,Optional
from pydantic import BaseModel, Field


class TicketInfo(BaseModel):
    """
    工单信息，字段覆盖客服判断处理进度和优先级最常用到的几项。
    user_id 和 order_no 记录这张工单涉及的用户与订单，客服拿到工单号之后
    可以顺着这两个字段去查用户资料和订单信息。
    """
    ticket_no: str = Field(description="工单号")
    title: str = Field(description="工单标题，概括用户诉求")
    status: Literal["待处理", "处理中", "已解决", "已关闭"] = Field(description="工单当前处理状态")
    priority: Literal["低", "中", "高", "紧急"] = Field(description="工单优先级")
    assignee: str = Field(description="当前负责处理的客服姓名，未分配时为“未分配”")
    user_id: Optional[str] = Field(default=None, description="关联的用户 ID，未核实时为空")
    order_no: Optional[str] = Field(default=None, description="关联的订单号，未核实时为空")
