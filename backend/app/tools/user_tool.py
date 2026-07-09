from langchain_core.tools import tool
from app.db.session import SessionLocal
from app.models.user import UserModel


@tool
def query_user(user_id: str) -> dict:
    """
    根据用户 ID 查询用户的姓名、等级和手机号，用户 ID 是形如 U10001 的字符串，通常需要先从用户自述或者已经查到的订单、工单信息里获得，不要直接把订单号或者工单号当成用户 ID 传入
    """
    db = SessionLocal()
    try:
        user = db.query(UserModel).filter(
            UserModel.user_id == user_id).first()
        if user is None:
            return {"error": f"未找到用户 {user_id}，请确认用户 ID 是否正确。"}
        return {
            "user_id": user.user_id,
            "name": user.name,
            "level": user.level,
            "phone": user.phone,
        }
    finally:
        db.close()
