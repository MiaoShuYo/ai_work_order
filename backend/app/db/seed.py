from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.logistics import LogisticsModel
from app.models.payment import PaymentModel
from app.models.order import OrderModel
from app.models.ticket import TicketModel
from app.models.user import UserModel
from app.models.chat_session import ChatSessionModel
from app.models.chat_message import ChatMessageModel


def seed_initial_data(db: Session) -> None:
    """
    把演示用的业务数据插入数据库，每个表只在为空时执行，
    避免应用重启导致主键冲突。老库里没有关联字段的工单会补一次回填，保证幂等。
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

    if db.query(UserModel).count() == 0:
        db.add_all(
            [
                UserModel(user_id="U10001", name="张伟",
                          level="VIP", phone="138****5566"),
                UserModel(user_id="U10002", name="李娜",
                          level="普通", phone="139****2233"),
            ]
        )

    if db.query(TicketModel).count() == 0:
        db.add_all(
            [
                TicketModel(
                    ticket_no="T20260615004",
                    title="发票开具咨询",
                    status="已解决",
                    priority="低",
                    assignee="王芳",
                    user_id="U10001",
                ),
                TicketModel(
                    ticket_no="T20260701001",
                    title="订单发货延迟投诉",
                    status="处理中",
                    priority="高",
                    assignee="王芳",
                    user_id="U10001",
                    order_no="202606050002",
                ),
                TicketModel(
                    ticket_no="T20260702002",
                    title="账号无法登录",
                    status="待处理",
                    priority="紧急",
                    assignee="未分配",
                    user_id="U10002",
                ),
                TicketModel(
                    ticket_no="T20260703003",
                    title="退款已到账确认",
                    status="已解决",
                    priority="低",
                    assignee="王芳",
                    user_id="U10002",
                    order_no="202606050001",
                ),
            ]
        )
    else:
        # Day 12 之前建过库的老数据没有关联字段，只回填一次，重复重启不会反复执行
        if db.query(TicketModel).filter(TicketModel.user_id.is_(None)).count() > 0:
            for ticket_no, user_id, order_no in [
                ("T20260615004", "U10001", None),
                ("T20260701001", "U10001", "202606050002"),
                ("T20260702002", "U10002", None),
            ]:
                ticket = db.query(TicketModel).filter(
                    TicketModel.ticket_no == ticket_no).first()
                if ticket is not None:
                    ticket.user_id = user_id
                    ticket.order_no = order_no

    if db.query(PaymentModel).count() == 0:
        db.add_all(
            [
                PaymentModel(
                    order_no="202606050002",
                    pay_no="ALIPAY20260528880001",
                    pay_type="支付宝",
                    amount=Decimal("300.00"),
                    pay_time="2026-05-28 14:32:00",
                ),
                PaymentModel(
                    order_no="202606050002",
                    pay_no="WECHAT20260602090002",
                    pay_type="微信支付",
                    amount=Decimal("999.00"),
                    pay_time="2026-06-02 20:15:00",
                ),
                PaymentModel(
                    order_no="202606050001",
                    pay_no="ALIPAY20260601990001",
                    pay_type="支付宝",
                    amount=Decimal("688.00"),
                    pay_time="2026-06-01 09:12:00",
                ),
            ]
        )

    if db.query(LogisticsModel).count() == 0:
        db.add_all(
            [
                LogisticsModel(
                    order_no="202606050002",
                    step_no=1,
                    time="2026-06-04 18:20:00",
                    location="杭州云仓",
                    description="快件已揽收，承运商为顺丰速运",
                ),
                LogisticsModel(
                    order_no="202606050002",
                    step_no=2,
                    time="2026-06-05 09:15:00",
                    location="杭州转运中心",
                    description="快件到达【杭州转运中心】",
                ),
                LogisticsModel(
                    order_no="202606050002",
                    step_no=3,
                    time="2026-06-05 21:30:00",
                    location="杭州转运中心",
                    description="快件已装车，发往【上海转运中心】",
                ),
            ]
        )

    if db.query(ChatSessionModel).count() == 0:
        demo_session = ChatSessionModel(
            session_id="demo-session-0001",
            thread_id="demo-thread-0001",
            title="订单发货延迟咨询",
            ticket_no=None,
            created_at="2026-07-05 09:30:00",
            updated_at="2026-07-05 09:30:00"
        )
        db.add(demo_session)
        db.add_all(
            [
                ChatMessageModel(
                    session_id="demo-session-0001",
                    thread_id="demo-thread-0001",
                    seq_no=1,
                    role="user",
                    content="你好，我有个订单一直没收到，能帮我看看吗？",
                    extra=None,
                    created_at="2026-07-05 09:30:00",
                ),
                ChatMessageModel(
                    session_id="demo-session-0001",
                    thread_id="demo-thread-0001",
                    seq_no=2,
                    role="assistant",
                    content="您好，请提供一下订单号，我帮您查询物流状态。",
                    extra=None,
                    created_at="2026-07-05 09:30:20",
                ),
                ChatMessageModel(
                    session_id="demo-session-0001",
                    thread_id="demo-thread-0001",
                    seq_no=3,
                    role="user",
                    content="订单号是 202606050002",
                    extra=None,
                    created_at="2026-07-05 09:31:40",
                ),
                ChatMessageModel(
                    session_id="demo-session-0001",
                    thread_id="demo-thread-0001",
                    seq_no=4,
                    role="assistant",
                    content=(
                        "已为您查询到订单 202606050002 状态为已发货、已出库，"
                        "物流最新轨迹停留在 6 月 5 日晚从杭州转运中心发往上海转运中心，"
                        "确实存在运输停滞，建议联系承运商核实干线运输情况。"
                    ),
                    extra=None,
                    created_at="2026-07-05 09:32:00",
                ),
            ]
        )

    db.commit()
