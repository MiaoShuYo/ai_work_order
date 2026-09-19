from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


class SessionInfo(BaseModel):
    """
    会话概要，左侧会话列表和创建接口用这个结构
    """

    session_id: str = Field(description="会话资源 ID")
    thread_id: str = Field(description="记忆线程 ID")
    title: str = Field(description="会话标题，首轮对话后自动生成")
    ticket_no: Optional[str] = Field(default=None, description="关联工单号，未关联时为空")
    created_at: str = Field(description="创建时间，格式 yyyy-MM-dd HH:mm:ss")
    updated_at: str = Field(description="最近活跃时间，列表按它倒序")


class SessionMessageItem(BaseModel):
    """
    会话里的一条消息。用户消息只填 role 和 content，
    AI 消息的意图、工具调用和引用来源从 extra JSON 平铺出来。
    """
    
    role: Literal["user", "assistant"]
    content: str
    intent: Optional[str] = Field(default=None, description="结构化回答的业务意图")
    confidence: Optional[float] = Field(default=None, description="回答置信度")
    need_human: Optional[bool] = Field(default=None, description="是否建议转人工")
    suggested_actions: list[str] = Field(default_factory=list)
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    sources: list[dict[str, Any]] = Field(default_factory=list)
    task_intent: Optional[dict[str, Any]] = Field(
        default=None, description="Day 11 的六类任务意图识别结果"
    )
    created_at: str
