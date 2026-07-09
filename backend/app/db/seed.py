from sqlalchemy.orm import Session
from app.models.order import OrderModel
from app.models.ticket import TicketModel
from app.models.user import UserModel


def seed_initial_data(db: Session) -> None:
    """
    把 Day 4、Day 5 里原本写死在内存字典里的示例数据插入数据库，只在表为空时执行，
    避免每次应用重启都重复插入导致主键冲突。
    """
    if db.query(OrderModel).count() == 0:
        db.add_all(
            [
                OrderModel(order_no="202606050001", status="待发货",
                           pay_status="已支付", logistics_status="未出库"),
                OrderModel(order_no="202606050002", status="已发货",
                           pay_status="已支付", logistics_status="已出库"),
            ]
        )
        db.commit()

    if db.query(TicketModel).count() == 0:
        db.add_all(
            [
                TicketModel(
                    ticket_no="T20260701001",
                    title="订单发货延迟投诉",
                    status="处理中",
                    priority="高",
                    assignee="王芳",
                ),
                TicketModel(
                    ticket_no="T20260702002",
                    title="账号无法登录",
                    status="待处理",
                    priority="紧急",
                    assignee="未分配",
                ),
            ]
        )
        db.commit()

    if db.query(UserModel).count() == 0:
        db.add_all(
            [
                UserModel(user_id="U10001", name="张伟",
                          level="VIP", phone="138****5566"),
                UserModel(user_id="U10002", name="李娜",
                          level="普通", phone="139****2233"),
            ]
        )

    db.commit()
