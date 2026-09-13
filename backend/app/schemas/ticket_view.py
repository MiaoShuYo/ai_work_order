from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.logistics import LogisticsInfo
from app.schemas.order import OrderInfo
from app.schemas.payment import PaymentInfo
from app.schemas.ticket import TicketInfo
from app.schemas.user import UserInfo


class TicketListItem(BaseModel):
    """
    工单列表行：工单字段加关联用户姓名，user_name 是联表拼出来的冗余展示字段，
    列表页不需要一整棵用户对象。
    """
    ticket_no: str = Field(description="工单号")
    title: str = Field(description="工单标题")
    status: str = Field(description="处理状态")
    priority: str = Field(description="优先级")
    assignee: str = Field(description="负责人")
    user_id: Optional[str] = Field(default=None, description="关联用户 ID")
    user_name: Optional[str] = Field(default=None, description="关联用户姓名，列表页示用")
    order_no: Optional[str] = Field(default=None, description="关联订单号")


class TicketDetail(BaseModel):
    """
    工单详情聚合视图：一张工单及其关联的用户、订单、支付、物流与历史工单，
    嵌套结构对应详情页要分区渲染的六个信息块。
    """

    ticket: TicketInfo = Field(description="工单基础信息")
    user: Optional[UserInfo] = Field(
        default=None, description="关联用户，未关联或查不到时为空")
    order: Optional[OrderInfo] = Field(
        default=None, description="关联订单，工单没有关联订单时为空")
    payments: list[PaymentInfo] = Field(
        default_factory=list, description="订单的支付流水，无流水时为空列表")
    logistics: Optional[LogisticsInfo] = Field(
        default=None, description="订单的物流轨迹，无轨迹时为空")
    history: list[TicketInfo] = Field(
        default_factory=list, description="同一用户的其他工单，按新到旧排列")
