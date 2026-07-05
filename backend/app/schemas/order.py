from typing import Literal
from pydantic import BaseModel, Field


class OrderInfo(BaseModel):
    """
    订单查询结果，字段覆盖发货、支付、物流三个客服最关心的维度
    """
    order_no: str = Field(description="订单号")
    status: Literal["待发货", "已发货", "已完成", "已取消"] = Field(description="订单当前状态")
    pay_status: Literal["已支付", "未支付"] = Field(description="支付状态")
    logistics_status: Literal["未出库", "已出库", "已签收"] = Field(description="物流状态")
