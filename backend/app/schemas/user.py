from typing import Literal
from pydantic import BaseModel, Field


class UserInfo(BaseModel):
    """
    用户基本信息，等级字段直接决定客服能给到的加急、退款等权限范围
    """
    user_id: str = Field(description="用户唯一标识")
    name: str = Field(description="用户姓名")
    level: Literal["普通", "VIP", "SVIP"] = Field(description="用户等级")
    phone: str = Field(description="手机号，中间四位已脱敏，格式如 138****5566")
