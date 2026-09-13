from sqlalchemy import Column, Numeric, String
from app.db.base import Base

class PaymentModel(Base):
    """
    支付流水表，一个订单可以有多条支付记录（例如先付定金再付尾款），
    用订单号 + 支付流水号做联合主键。金额用 Numeric 精确存小数，
    避免浮点数在展示和后续对账时出现精度问题。
    """

    __tablename__ = "payments"

    order_no= Column(String,primary_key=True)
    pay_no = Column(String, primary_key=True)
    pay_type= Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    pay_time= Column(String, nullable=False)