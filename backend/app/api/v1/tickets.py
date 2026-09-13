from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.logistics import LogisticsModel
from app.models.order import OrderModel
from app.models.payment import PaymentModel
from app.models.ticket import TicketModel
from app.models.user import UserModel
from app.schemas.logistics import LogisticsInfo, LogisticsStep
from app.schemas.order import OrderInfo
from app.schemas.payment import PaymentInfo
from app.schemas.ticket import TicketInfo
from app.schemas.ticket_view import TicketListItem, TicketDetail
from app.schemas.user import UserInfo

router = APIRouter(prefix="/api/v1/tickets", tags=["tickets"])


def _to_ticket_info(ticket: TicketModel) -> TicketInfo:
    """
    ORM 工单行 -> 基础 schema，字段一一对应。列表和详情两处都要把工单行转成 TicketInfo，抽成函数避免两处各写一遍字段映射。
    """
    return TicketInfo(
        ticket_no=ticket.ticket_no,
        title=ticket.title,
        status=ticket.status,
        priority=ticket.priority,
        assignee=ticket.assignee,
        user_id=ticket.user_id,
        order_no=ticket.order_no
    )


def _to_user_info(user: UserModel) -> UserInfo:
    return UserInfo(
        user_id=user.user_id,
        name=user.name,
        level=user.level,
        phone=user.phone
    )


def _to_order_info(order: OrderModel) -> OrderInfo:
    return OrderInfo(
        order_no=order.order_no,
        status=order.status,
        pay_status=order.pay_status,
        logistics_status=order.logistics_status
    )


def _to_payment_info(payment: PaymentModel) -> PaymentInfo:
    return PaymentInfo(
        order_no=payment.order_no,
        pay_no=payment.pay_no,
        pay_type=payment.pay_type,
        # Numeric 列读出来是 Decimal，JSON 不认，先格式化成两位小数的字符串
        amount=f"{payment.amount:.2f}",
        pay_time=payment.pay_time
    )


def _to_logistics_info(order_no: str, steps: list[LogisticsModel]) -> LogisticsInfo:
    return LogisticsInfo(
        order_no=order_no,
        steps=[LogisticsStep(
            time=step.time,
            location=step.location,
            description=step.description
        ) for step in steps],
    )


@router.get("", response_model=list[TicketListItem])
def list_tickets(db: Session = Depends(get_db)) -> list[TicketListItem]:
    """
    工单列表：工单号含日期，倒序就是新的在前。user_name 是一次性批量补查 users 表拼出来的，避免循环里逐行发查询。
    """
    tickets = db.query(TicketModel).order_by(
        TicketModel.ticket_no.desc()).all()
    user_ids = {ticket.user_id for ticket in tickets if ticket.user_id}
    users: dict[str, UserModel] = {}
    if user_ids:
        users = {
            user.user_id: user
            for user in db.query(UserModel).filter(UserModel.user_id.in_(user_ids)).all()
        }

    return [
        TicketListItem(
            ticket_no=ticket.ticket_no,
            title=ticket.title,
            status=ticket.status,
            priority=ticket.priority,
            assignee=ticket.assignee,
            user_id=ticket.user_id,
            user_name=users[ticket.user_id].name if ticket.user_id and ticket.user_id in users else None,
            order_no=ticket.order_no
        )
        for ticket in tickets
    ]


@router.get("/{ticket_no}", response_model=TicketDetail)
def get_ticket_detail(ticket_no: str, db: Session = Depends(get_db)) -> TicketDetail:
    """
    工单详情：以工单为根，向关联的用户、订单、支付、物流以及同用户的其他工单各查一次，组装成页面要用的聚合树。工单查不到时返回 404。
    """
    ticket = db.query(TicketModel).filter(
        TicketModel.ticket_no == ticket_no).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail=f"工单 {ticket_no} 不存在")

    user: Optional[UserInfo] = None
    if ticket.user_id:
        user_row = db.query(UserModel).filter(
            UserModel.user_id == ticket.user_id).first()
        if user_row is not None:
            user = _to_user_info(user_row)

    order: Optional[OrderInfo] = None
    payments: list[PaymentInfo] = []
    logistics: Optional[LogisticsInfo] = None
    if ticket.order_no:
        order_row = db.query(OrderModel).filter(
            OrderModel.order_no == ticket.order_no).first()
        if order_row is not None:
            order = _to_order_info(order_row)
            payment_rows = (
                db.query(PaymentModel)
                .filter(PaymentModel.order_no == ticket.order_no)
                .order_by(PaymentModel.pay_time)
                .all()
            )
            payments = [_to_payment_info(payment) for payment in payment_rows]
            step_rows = (
                db.query(LogisticsModel)
                .filter(LogisticsModel.order_no == ticket.order_no)
                .order_by(LogisticsModel.step_no)
                .all()
            )
            if step_rows:
                logistics = _to_logistics_info(ticket.order_no, step_rows)

    history: list[TicketInfo] = []
    if ticket.user_id:
        history_rows = (
            db.query(TicketModel)
            .filter(
                TicketModel.user_id == ticket.user_id,
                TicketModel.ticket_no != ticket_no
            )
            .order_by(TicketModel.ticket_no.desc())
            .all()
        )
        history = [_to_ticket_info(row) for row in history_rows]

    return TicketDetail(
        ticket=_to_ticket_info(ticket),
        user=user,
        order=order,
        payments=payments,
        logistics=logistics,
        history=history
    )
