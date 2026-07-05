from langchain_core.tools import tool
from app.schemas.order import OrderInfo

# 模拟订单数据源，真是项目这里会换成调用订单系统的 PRC 或者查询数据库

_MOCK_ORDERS: dict[str, OrderInfo] = {
    "202606050001": OrderInfo(
        order_no="202606050001",
        status="待发货",
        pay_status="已支付",
        logistics_status="未出库",
    ),
    "202606050002": OrderInfo(
        order_no="202606050002",
        status="已发货",
        pay_status="已支付",
        logistics_status="已出库",
    ),
}


@tool
def query_order(order_no: str) -> dict:
    """
    根据订单号查询订单的发货状态、支付状态和物流状态，订单号是形如 202606050001 的字符串。
    """
    order = _MOCK_ORDERS.get(order_no)
    if order is None:
        # 订单不存在时不抛出异常，而是返回一个带 error 字段的普通 dict，让模型能在最终回答里直接告诉用户没查到这个订单。
        # 如果这里抛异常，反而需要在 stream_chat 里额外区分这类业务性的“查无结果” 和真正的网络、序列化异常，没有必要让两种情况混在一起。
        return {"error": f"未找到订单 {order_no}，请确认订单号是否正确。"}
    return order.model_dump()
