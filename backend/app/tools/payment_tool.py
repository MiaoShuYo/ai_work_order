from langchain_core.tools import tool
from app.db.session import SessionLocal
from app.models.payment import PaymentModel


@tool
def query_payment(order_no: str) -> dict:
    """
    根据订单号查询该订单的支付流水，返回每笔支付的渠道、金额和支付时间。
    一个订单可能有多笔流水（例如定金、尾款分开支付），订单号是形如 202606050001 的字符串，
    通常来自用户自述或已查询到的订单、工单信息。
    """
    db = SessionLocal()
    try:
        payments = (
            db.query(PaymentModel)
            .filter(PaymentModel.order_no == order_no)
            .order_by(PaymentModel.pay_time)
            .all()
        )
        if not payments:
            return {"error": f"未找到订单 {order_no} 的支付流水，请确认订单是否已支付或订单号是否正确。"}
        return {
            "order_no": order_no,
            "payments": [
                {
                    "pay_no": payment.pay_no,
                    "pay_type": payment.pay_type,
                    "amount": f"{payment.amount:.2f}",
                    "pay_time": payment.pay_time
                }
                for payment in payments
            ]
        }
    finally:
        db.close()
