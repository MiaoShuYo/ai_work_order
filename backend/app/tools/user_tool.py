from langchain_core.tools import tool
from app.schemas.user import UserInfo

_MOCK_USERS: dict[str, UserInfo] = {
    "U10001": UserInfo(user_id="U10001", name="张伟", level="VIP", phone="138****5566"),
    "U10002": UserInfo(user_id="U10002", name="李娜", level="普通", phone="139****2233"),
}


@tool
def query_user(user_id: str) -> dict:
    """
    根据用户 ID 查询用户的姓名、等级和手机号，用户 ID 是形如 U10001 的字符串，通常需要先从用户自述或者已经查到的订单、工单信息里获得，不要直接把订单号或者工单号当成用户 ID 传入
    """
    user = _MOCK_USERS.get(user_id)
    if user is None:
        return {"error": f"未找到用户 {user_id}，请确认用户 ID 是否正确。"}
    return user.model_dump()
