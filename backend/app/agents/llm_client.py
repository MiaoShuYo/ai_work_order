import json
import os
from typing import AsyncGenerator

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from app.schemas.chat import ChatResponse, ToolCallResult
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

_SYSTEM_PROMPT = (
    "你是一个电商平台的智能客服助手，需要基于用户的问题给出结构化判断。"
    "intent 只能从 order_issue、account_issue、refund_request、general_inquiry、other 中选择一个，"
    "分别对应订单问题、账号问题、退款请求、一般咨询和其他情况。"
    "如果用户的问题涉及具体订单号的发货、支付或物流状态，调用 query_order 查询真实数据。"
    "如果用户提到了工单号或者想知道之前提交的工单处理进度，调用 query_ticket 查询。"
    "如果需要确认用户的身份、等级或者联系方式，调用 query_user 查询，用户 ID 通常需要先从对话里确认，不要凭空编造。"
    "如果用户的问题属于退款政策、发货时效、账号安全这类通用规则性问题，调用 search_knowledge_base 检索相关说明，"
    "不要凭记忆直接回答政策类问题。"
    "以上工具可以在同一轮对话里按需要多次调用，不要凭空编造任何工具没有返回过的数据。"
    "confidence 反映你对这次判断和回答的把握程度，如果问题描述模糊或者超出你的知识范围，"
    "应该给出较低的置信度并将 need_human 设为 true，提醒客服人员介入。"
    "suggested_actions 给出客服人员可以立刻执行的具体动作，不要给空泛的建议。"
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


async def stream_chat(messages: list[dict[str, str]]) -> AsyncGenerator[dict, None]:
    """
    驱动一次可能包含多轮、多种工具调用的对话，以事件流的形式产出中间过程和最终结果。
    """
    history: list[BaseMessage] = [SystemMessage(
        content=_SYSTEM_PROMPT), *_to_langchain_messages(messages)]
    collected_tool_calls: list[ToolCallResult] = []

    try:
        for _ in range(_MAX_TOOL_ITERATIONS):
            ai_message = await _llm_with_tools.ainvoke(history)

            if not ai_message.tool_calls:
                # 模型这一轮没有请求任何工具，说明它任务已经掌握了足够信息，直接跳出循环进入最终的结构化输出
                break
            history.append(ai_message)

            for tool_call in ai_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                yield {"type": "tool_call_start", "name": tool_name, "args": tool_args}

                tool = _TOOLS_BY_NAME.get(tool_name)
                tool_result = await tool.ainvoke(tool_args)
                
                yield {"type": "tool_call_end", "name": tool_name, "result": tool_result}
                collected_tool_calls.append(
                    ToolCallResult(
                        name=tool_name, args=tool_args, result=tool_result)
                )
                # ToolMessage 必须带上对应的 tool_call_id，模型才能把这条结果和他发起的那次调用对上号，尤其在一轮里并行调用多个工具时这一点不能省。
                history.append(
                    ToolMessage(
                        content=json.dumps(tool_result, ensure_ascii=False), tool_call_id=tool_call["id"])
                )
        else:
            # 在循环耗尽 _MAX_TOOL_ITERATIONS 次数，始终没有触发 break 时执行，说明模型一直在反复调用工具没有收敛，这里追加一条系统提示，逼着接下来的结构化输出必须直接给出结论
            history.append(SystemMessage(
                content="已达到最大工具调用次数，请基于目前已有的信息直接给出结论。"))

        final_response: ChatResponse = await _structured_llm.ainvoke(history)
        final_response.tool_calls = collected_tool_calls
        yield {"type": "final", "data": final_response.model_dump()}
    except Exception as exc:
        # 流已经开始推送之后不能再抛出 HTTPException 让FastAPI 转换成标准错误响应，响应头和部分事件很可能已经发给前端了，只能通过一个 error 事件通知调用方，由前端决定怎么在界面上呈现这次失败。
        yield {"type": "error", "message": str(exc)}
