import json
import os
from typing import AsyncGenerator

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from app.schemas.chat import ChatResponse, ToolCallResult
from app.schemas.knowledge import SourceInfo
from app.tools.knowledge_tool import search_knowledge_base
from app.tools.order_tool import query_order
from app.tools.ticket_tool import query_ticket
from app.tools.user_tool import query_user

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

# 结构化输出和工具调用不能共用同一个绑定后的模型实例，LangChain 官方文档在结构化输出一节特别提示过，预先 bind_tools 之后的模型不再支持叠加 with_structured_output，所以这里准备两个各司其职的模型实例，_llm_with_tools 只负责判断要不要调用工具、调用哪个工具，_structured_llm 只在拿到足够信息之后把自然语言整理成规定的 schema。
_TOOLS = [query_order, search_knowledge_base, query_ticket, query_user]
_llm_with_tools = _llm.bind_tools(_TOOLS)

# with_structured_output 默认（不传 include_raw）会直接返回校验通过的 ChatResponse 实例不需要自己再解析模型输出的原始文本，也不需要处理 include_raw=True 时才会出现的 {"raw","parsed","parsing_error"} 这种字典结构
_structured_llm = _llm.with_structured_output(ChatResponse)
_TOOLS_BY_NAME = {t.name: t for t in _TOOLS}

# 今天的场景可能需要先查用户、再查订单、再查关联工单，三轮工具调用已经把余量用的比较紧，调到 4 给正常的多工具协同流程留一点安全边际，真触发上限说明模型没有在合理的步数内收敛。
_MAX_TOOL_ITERATIONS = 4

_SYSTEM_PROMPT = """你是一个企业客服 AI 助手，可以帮助客服查询订单、工单、用户信息，以及从公司知识库中检索政策、产品说明等资料。

## 工具使用规范
如果用户的问题涉及具体订单号的发货、支付或物流状态，调用 query_order 查询真实数据。
如果用户提到了工单号或者想知道之前提交的工单处理进度，调用 query_ticket 查询。
如果需要确认用户的身份、等级或者联系方式，调用 query_user 查询，用户 ID 通常需要先从对话里确认，不要凭空编造。
如果用户的问题属于退款政策、发货时效、账号安全这类通用规则性问题，调用 search_knowledge_base 检索相关说明，不要凭记忆直接回答政策类问题。
以上工具可以在同一轮对话里按需要多次调用，不要凭空编造任何工具没有返回过的数据。

## 引用规范（重要）
当你使用知识库检索（search_knowledge_base）返回的片段来组织回答时，必须在回答中用 [数字] 标注每条关键信息的来源，数字对应片段列表中的序号。
例如，如果片段 1 来自售后政策文档、片段 2 来自退款规则文档，你的回答应该类似：

"根据售后政策，用户签收后 7 天内可申请无理由退款[1]，退款将在 3 个工作日内原路退回[2]。"

引用标注要紧跟被引用的那句话，不要把所有标注堆在段落末尾，也不要漏掉任何一条来自知识库的信息。如果某条信息是你自己的通用知识而非来自检索结果，不要给它加引用标注。"""

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


async def stream_chat(messages: list[dict[str, str]], conversation_id: str = "") -> AsyncGenerator[dict, None]:
    """
    流式处理一轮对话，在最终回答之后会额外发送 sources 事件携带引用来源。
    """
    full_messages = [SystemMessage(content=_SYSTEM_PROMPT)]+list(messages)

    # 收集本轮对话中知识库检索返回的所有片段，用于最终生成 sources事件
    collected_sources: list[SourceInfo] = []
    # 收集本轮对话中所有工具调用的记录，最终挂到 ChatResponse.tool_calls 上让前端展示
    collected_tool_calls: list[ToolCallResult] = []

    iteration = 0
    while iteration < _MAX_TOOL_ITERATIONS:
        iteration += 1
        response: AIMessage = await _llm_with_tools.ainvoke(full_messages)

        if not response.tool_calls:
            # 没有工具调用，生成最终回答
            final_response: ChatResponse = await _structured_llm.ainvoke(full_messages)
            final_response.tool_calls = collected_tool_calls

            yield {"type": "final", "data": final_response.model_dump()}

            # 如果有收集到知识库来源，在 final 之后紧跟着发送 sources 事件
            if collected_sources:
                yield {
                    "type": "sources",
                    "data": {
                        "conversation_id": conversation_id,
                        "sources": [s.model_dump() for s in collected_sources]
                    },
                }
            return
        # 处理工具调用
        full_messages.append(response)
        for tool_call in response.tool_calls:
            name = tool_call["name"]
            args = tool_call["args"]
            tool_func = _TOOLS_BY_NAME.get(name)
            if tool_func is None:
                continue

            yield {"type": "tool_call_start", "name": name, "args": args}

            result = tool_func.invoke(args)
            yield {"type": "tool_call_end", "name": name, "result": result}

            full_messages.append(
                ToolMessage(
                    content=json.dumps(result, ensure_ascii=False),
                    tool_call_id=tool_call["id"]
                )
            )
            collected_tool_calls.append(
                ToolCallResult(name=name, args=args, result=result)
            )

            # 如果是知识库检索，把返回的片段收集起来
            if name == "search_knowledge_base" and isinstance(result, dict):
                for snippet in result.get("snippets", []):
                    collected_sources.append(
                        SourceInfo(
                            index=snippet["index"],
                            filename=snippet["filename"],
                            chunk_index=snippet["chunk_index"],
                            content=snippet["content"],
                            score=snippet["score"],
                            page=snippet.get("page")
                        )
                    )
    # 超出最大迭代次数，强制生成回答
    full_messages.append(
        SystemMessage(content="已达到最大工具调用次数，请基于目前已有的信息直接给出结论。")
    )

    final_response: ChatResponse = await _structured_llm.ainvoke(full_messages)
    final_response.tool_calls = collected_tool_calls

    yield {"type": "final", "data": final_response.model_dump()}

    if collected_sources:
        yield {
            "type": "sources",
            "data": {
                "conversation_id": conversation_id,
                "sources": [s.model_dump() for s in collected_sources],
            },
        }
