from typing import Literal
from pydantic import BaseModel, Field

class PaymentInfo(BaseModel):
    """
    一笔支付流水，一个订单可能对应多笔（定金、尾款分开支付）。
    """
    order_no: str = Field(description="订单号")
    pay_no: str = Field(description="支付渠道返回的流水号")
    pay_type: Literal["支付宝", "微信支付", "银行卡"] = Field(description="支付渠道")
    amount:str= Field(description="本次支付金额，单位元，保留两位小数，例如 300.00")
    pay_time: str = Field(description="支付时间，格式 yyyy-MM-dd HH:mm:ss")