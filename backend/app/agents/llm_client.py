import os

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI

_MODEL_NAME = os.getenv("CHAT_MODEL_NAME", "deepseek-ai/DeepSeek-V4-Pro")

# ChatOpenAI 在模块加载时实例化一次并全局复用，FastAPI 的路由函数是 async def，
# ChatOpenAI 的 ainvoke 走的是异步调用，不会阻塞事件循环。
_llm = ChatOpenAI(
    model=_MODEL_NAME,
    api_key=os.getenv("OPENAI_API_KEY"),
    # 如果公司内部走的是私有部署或者国内厂商提供的兼容接口，改这里的 base_url 即可，
    # 不用改调用逻辑，这也是选择 OpenAI 协议兼容接口的原因，LangChain 的 ChatOpenAI 本身就是按这个给协议对接的，换厂商基本上不用碰代码
    base_url=os.getenv("OPENAI_BASE_URL") or None
)

_ROLE_TO_MESSAGE = {
    "user": HumanMessage,
    "assistant": AIMessage
}


def _to_langchain_messages(messages: list[dict[str, str]]) -> list[BaseMessage]:
    """
    把前端传来的 role/content 字典转换成 LangChain 的消息对象列表
    """
    return [_ROLE_TO_MESSAGE[message["role"]](content=message["content"])for message in messages
            ]


async def call_llm(messages: list[dict[str, str]]) -> str:
    """
    把消息历史转给大模型，返回纯文本回复
    """
    response = await _llm.ainvoke(_to_langchain_messages(messages))
    return response.content
