from sqlalchemy import Column, String
from app.db.base import Base


class OrderModel(Base):
    """
    订单表，字段和 schemas/order.py 里的 OrderInfo 一一对应，
    但这里是数据库表结构，不负责接口层的校验，取值范围的限制交给写入时的业务代码保证。
    """
    __tablename__ = "orders"
    order_no = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    pay_status = Column(String, nullable=False)
    logistics_status = Column(String, nullable=False)
