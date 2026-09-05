from typing import Literal
from pydantic import BaseModel, Field

# 六种任务类型涵盖了当前系统需要区分的所有用户意图，后续如果有新的业务场景再扩展这个枚举，新增枚举值需要同步更新 intent_agent.py 中的系统提示词示例，否则模型不会主动输出新类型。
IntentType = Literal[
    "knowledge_qa",
    "order_query",
    "complaint_handle",
    "ticket_create",
    "refund_advice",
    "transfer_human",
]

# 每种任务类型在前端展示时的中文标签和颜色，放在 schema 文件里而不是前端硬编码，保证后端新增意图类型时只需要改一处配置，前端通过 intent 事件的 intent 值映射到对应标签即可。
INTENT_LABELS: dict[str, dict[str, str]] = {
    "knowledge_qa": {"label": "知识问答", "color": "#2563eb"},
    "order_query": {"label": "订单查询", "color": "#059669"},
    "complaint_handle": {"label": "投诉处理", "color": "#dc2626"},
    "ticket_create": {"label": "工单创建", "color": "#d97706"},
    "refund_advice": {"label": "退款建议", "color": "#7c3aed"},
    "transfer_human": {"label": "转人工", "color": "#6b7280"},
}


class IntentResult(BaseModel):
    """
    意图识别结果，由 classify_intent 返回，供 stream_chat 和前端使用。
    """

    intent: IntentType = Field(description="识别出的任务类型，六选一")
    confidence: float = Field(
        ge=0, le=1, description="本次判断的置信度，0 到 1 之间，越高表示模型越确定")
    reasoning: str = Field(
        default="", description="一句话说明判断依据，如'用户提到了物流慢和投诉字样'")
    need_human: bool = Field(
        default=False, description="是否建议转人工，由调用方根据置信度阈值设置，不由模型决定")
