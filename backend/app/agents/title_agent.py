import os
from langchain_openai import ChatOpenAI

# 标题生成比意图分类还简单，优先沿用意图模型的配置，一个轻量模型足够
_MODEL_NAME = os.getenv(
    "TITLE_MODEL_NAME",
    os.getenv("INTENT_MODEL_NAME", os.getenv(
        "CHAT_MODEL_NAME", "deepseek-ai/DeepSeek-V4-Pro"))
)

_title_llm = ChatOpenAI(
    model=_MODEL_NAME,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL") or None,
    temperature=0,
    max_tokens=32,  # 12 个字以内的标题，32 token 绰绰有余
    request_timeout=10,
    max_retries=0,  # 标题失败直接走截断降级，不重试浪费时间
)

_TITLE_SYSTEM_PROMPT = """你是会话标题生成器。根据用户的第一条消息，生成一个不超过 12 个汉字的会话标题。
标题要概括用户要办的事，优先保留订单号、工单号这类关键信息，例如"订单物流停滞咨询""发票开具问题"。
不要输出标点符号、引号、书名号，不要加"关于""的问题""咨询一下"这类外壳，直接输出标题文本本身。"""


async def generate_title(user_message: str) -> str:
    """
    把用户首条消息改写成短标题。调用方负责捕获异常并做截断降级。
    """
    response = await _title_llm.ainvoke(
        [
            {"role": "system", "content": _TITLE_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )
    title = str(response.content).strip().strip("\"'“”‘’《》")
    return title
