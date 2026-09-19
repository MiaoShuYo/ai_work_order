from typing import Literal
from pydantic import BaseModel, Field


class ToolCallResult(BaseModel):
    """
    一次工具调用的完整记录，args 和 result 都是原始 dict，方便前端直接渲染成卡片。
    """
    name: str = Field(description="被调用的工具名")
    args: dict = Field(description="调用工具时传入的参数")
    result: dict = Field(description="工具返回的结果")


class ChatResponse(BaseModel):
    """
    结构化的 AI 回复，字段口径与 Day 4 引入时保持一致。
    """
    intent: Literal[
        "order_issue", "account_issue", "refund_request", "general_inquiry", "other"
    ] = Field(description="用户问题所属的业务类型")
    answer: str = Field(description="面向用户展示的回答内容")
    confidence: float = Field(
        ge=0, le=1, description="AI 对本次判断的置信度，取值范围 0 到 1")
    need_human: bool = Field(description="是否建议转人工处理")
    suggested_actions: list[str] = Field(
        default_factory=list, description="给客服的后续操作建议，不展示给终端用户"
    )
    tool_calls: list[ToolCallResult] = Field(
        default_factory=list, description="本轮实际发生的工具调用，由循环代码拼装"
    )


class ChatRequest(BaseModel):
    """
    聊天请求。Day 13 起只传会话 ID 和用户刚发的这一条消息，
    历史由后端凭 session_id 从数据库恢复，前端不再整包回传消息列表。
    """

    session_id: str = Field(min_length=1, description="会话 ID，由 POST /api/v1/sessions 创建")
    message: str = Field(min_length=1, description="用户本次输入的文本")
