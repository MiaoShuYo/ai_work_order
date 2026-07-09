from langchain_core.tools import tool
from app.db.session import SessionLocal
from app.models.order import OrderModel


@tool
def query_order(order_no: str) -> dict:
    """
    根据订单号查询订单的发货状态、支付状态和物流状态，订单号是形如 202606050001 的字符串。
    """
    # 工具调用发生在 Agent 循环内部，不在 FastAPI 的请求-响应依赖注入路径上，没法复用 get_db，所以这里自己开一个会话，用完在 finally 里关闭。
    db = SessionLocal()
    try:
        order = db.query(OrderModel).filter(
            OrderModel.order_no == order_no).first()
        if order is None:
            return {"error": f"未找到订单 {order_no}，请确认订单号是否正确。"}
        return {
            "order_no": order.order_no,
            "status": order.status,
            "pay_status": order.pay_status,
            "logistics_status": order.logistics_status,
        }
    finally:
        db.close()
