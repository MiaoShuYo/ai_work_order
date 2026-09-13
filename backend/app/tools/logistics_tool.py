from langchain_core.tools import tool
from app.db.session import SessionLocal
from app.models.logistics import LogisticsModel


@tool
def query_logistics(order_no: str) -> dict:
    """
    根据订单号查询该订单的物流轨迹，按时间从早到晚返回每一个节点（时间、地点、动作描述），
    用于判断包裹当前停在哪里、是否出现运输延迟。订单号是形如 202606050001 的字符串。
    """
    db = SessionLocal()
    try:
        steps = (
            db.query(LogisticsModel)
            .filter(LogisticsModel.order_no == order_no)
            .order_by(LogisticsModel.step_no)
            .all()
        )
        if not steps:
            return {"error": f"未找到 {order_no} 的物流轨迹，请确认订单是否已经出库或订单号是否正确。"}
        return {
            "order_no": order_no,
            "steps": [
                {
                    "time": step.time,
                    "location": step.location,
                    "description": step.description
                }
                for step in steps
            ],
        }
    finally:
        db.close()
