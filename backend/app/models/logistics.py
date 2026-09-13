from sqlalchemy import Column,Integer,String
from app.db.base import Base

class LogisticsModel(Base):
    """
    物流轨迹表，一个订单对应一条时间轴上的多个节点，
    用订单号 + 步骤序号做联合主键，按 step_no 从小到大就能还原完整轨迹。
    """

    __tablename__ = "logistics"

    order_no=Column(String,primary_key=True)
    step_no=Column(Integer,primary_key=True)
    time=Column(String,nullable=False)
    location=Column(String,nullable=False)
    description=Column(String,nullable=False)
