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
    聊天响应消息
    """
    reply: str