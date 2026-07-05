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


class ToolCallResult(BaseModel):
    """
    一次工具调用的完整记录，args 和 result 都是原始 dict，方便前端直接渲染成卡片。
    """
    name: str = Field(description="被调用的工具名")
    args: dict = Field(description="调用工具时传入的参数")
    result: dict = Field(description="工具返回的结果")


class ChatResponse(BaseModel):
    """
    结构化的 AI 回复。
    intent 决定这条回复归到哪一类问题；
    answer 是真正要展示给终端用户的文本；
    confidence 和 need_human 共同决定客服要不要介入；
    suggested_actions 只给客服看，不会出现在任何可见的界面上；
    tool_calls 记录这轮对话里实际发生过的工具调用，由后端在执行完工具后拼装，不依赖模型在最终回答里复述调用细节。
    """
    intent: Literal["order_issue", "account_issue", "refund_request",
                    "general_inquiry", "other"] = Field(description="用户问题所属的业务类型")
    answer: str = Field(description="面向用户展示的回答")
    confidence: float = Field(
        ge=0, le=1, description="AI 对本次判断的置信度，取值范围 0 到 1")
    need_human: bool = Field(description="是否建议转人工处理")
    suggested_actions: list[str] = Field(
        default_factory=list, description="给客服的后续操作建议，不展示给终端用户")
    tool_calls: list[ToolCallResult] = Field(
        default_factory=list, description="本轮对话实际发生的工具调用记录")
