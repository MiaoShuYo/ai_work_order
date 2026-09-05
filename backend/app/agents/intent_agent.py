import os
from langchain_openai import ChatOpenAI
from app.schemas.intent import IntentResult

# 意图识别用独立的小模型即可，不需要和主 Agent 用同一个大模型，分类任务的难度远低于生成带引用的结构化回答，用轻量模型可以降低延迟和成本。
_MODEL_NAME = os.getenv("INTENT_MODEL_NAME", os.getenv(
    "CHAT_MODEL_NAME", "deepseek-ai/DeepSeek-V4-Pro"))

_intent_llm = ChatOpenAI(
    model=_MODEL_NAME,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL") or None,
    temperature=0,  # 分类任务不需要随机性
    max_tokens=512,  # 意图分类输出只是一个小 JSON，512 token 足够，同时限制推理模型的 reasoning 长度
    request_timeout=10,  # 10 秒超时，意图分类应该很快
    max_retries=0,  # 不重试，失败直接降级
)



_structured_intent_llm = _intent_llm.with_structured_output(IntentResult)

_INTENT_SYSTEM_PROMPT = """你是一个意图分类器，负责判断用户在客服对话中的意图类型。你只做分类，不回答问题、不执行操作、不提供建议。

## 六种意图类型

- knowledge_qa：用户问的是政策、规则、产品说明、操作指南等知识类问题，希望通过查资料获得答案。例如"7天无理由退款政策是什么""怎么修改绑定的手机号"。
- order_query：用户想查询某个订单的状态、物流、支付情况。例如"帮我查一下订单 ORD-20260721-001""我的订单发货了吗"。
- complaint_handle：用户表达了不满、投诉或抱怨。例如"物流太慢了我要投诉""已经等了三天了还没处理"。
- ticket_create：用户明确要求创建一张新工单来记录问题或发起流程。例如"帮我建一个工单处理换货""我要申请售后维修"。
- refund_advice：用户询问退款相关的问题，或者明确表达了退款意愿。例如"我想退款""这个订单能退吗""退款什么时候到账"。
- transfer_human：用户明确要求转人工客服，或者表达了"不想和机器人说话"的态度。例如"转人工""我要找真人客服""你们到底有没有人工"。

## 判断规则

1. 如果用户在抱怨时也提到了订单号，按优先级判断为 complaint_handle（投诉优先于订单查询），因为用户的情绪需要被优先处理。
2. 如果用户问了退款政策又表达了退款意愿，判断为 refund_advice 而不是 knowledge_qa（行动意愿优先于知识查询）。
3. 如果用户措辞含糊、信息不足，仍然给出你最倾向的判断，confidence 设为 0.5 到 0.7 之间，并在 reasoning 中说明不确定的原因。
4. 禁止输出 intent 以外的字段，不要尝试回答用户的问题。"""


async def classify_intent(user_message: str) -> IntentResult:
    """
    对用户输入做意图分类，返回 IntentResult。user_message 应该只包含用户最新一条消息的文本，不需要传历史消息，意图识别仅依赖当前输入即可做出足够准确的判断。
    """
    messages = [
        {"role": "system", "content": _INTENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]
    result: IntentResult = await _structured_intent_llm.ainvoke(messages)
    return result
