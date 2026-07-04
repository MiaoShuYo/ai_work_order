from typing import Literal
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """
    单条对话消息，role 只区分用户和 AI 两种角色，系统提示词由后端在调用模型时自行拼装
    """
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    """
    聊天请求消息，包含全部的消息
    """
    # 这里传的是完整历史而不是单条消息，因为今天的后端不维护会话状态
    # 多轮上下文靠前端把之前的消息一并带上来实现
    messages: list[ChatMessage] = Field(min_length=1)


class ChatResponse(BaseModel):
    """
    结构化的 AI 回复。intent 决定这条回复归到哪一类问题，answer 是真正要展示给终端用户的文本，confidence 和 need_human 共同决定客服要不要介入，suggested_actions 只给客服看，不会出现在任何可见的界面上。
    """
    intent: Literal["order_issue", "account_issue", "refund_request",
                    "general_inquiry", "other"] = Field(description="用户问题所属的业务类型")
    answer: str = Field(description="面向用户展示的回答")
    confidence: float = Field(
        ge=0, le=1, description="AI 对本次判断的置信度，取值范围 0 到 1")
    need_human: bool = Field(description="是否建议转人工处理")
    suggested_actions: list[str] = Field(
        default_factory=list, description="给客服的后续操作建议，不展示给终端用户")
