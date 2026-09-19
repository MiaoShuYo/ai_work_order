import json
import os
from typing import AsyncGenerator

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from app.schemas.chat import ChatResponse, ToolCallResult
from app.schemas.knowledge import SourceInfo
from app.schemas.intent import IntentResult, INTENT_LABELS, IntentType
from app.agents.intent_agent import classify_intent
from app.tools.knowledge_tool import search_knowledge_base
from app.tools.order_tool import query_order
from app.tools.ticket_tool import query_ticket
from app.tools.user_tool import query_user
from app.tools.logistics_tool import query_logistics
from app.tools.payment_tool import query_payment
from app.agents.title_agent import generate_title
from app.db.session import SessionLocal
from app.repositories.session_repository import SessionRepository
from app.services.memory_service import ConversationMemory

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
_TOOLS = [query_order, search_knowledge_base, query_ticket,
          query_user, query_payment, query_logistics]
_llm_with_tools = _llm.bind_tools(_TOOLS)

# with_structured_output 默认（不传 include_raw）会直接返回校验通过的 ChatResponse 实例不需要自己再解析模型输出的原始文本，也不需要处理 include_raw=True 时才会出现的 {"raw","parsed","parsing_error"} 这种字典结构
_structured_llm = _llm.with_structured_output(ChatResponse)
_TOOLS_BY_NAME = {t.name: t for t in _TOOLS}

# 今天的场景可能需要先查用户、再查订单、再查关联工单，三轮工具调用已经把余量用的比较紧，调到 4 给正常的多工具协同流程留一点安全边际，真触发上限说明模型没有在合理的步数内收敛。
_MAX_TOOL_ITERATIONS = 4

# 置信度阈值，低于此值时系统建议转人工，数值来自业务方的要求，他们希望 AI 在拿不准时宁可不说也不要乱说。
_CONFIDENCE_THRESHOLD = float(os.getenv("INTENT_CONFIDENCE_THRESHOLD", "0.6"))

_AGENT_SYSTEM_PROMPT = """你是一个企业客服 AI 助手，可以帮助客服查询订单、工单、用户信息，以及从公司知识库中检索政策、产品说明等资料。

## 工具使用规范
如果用户的问题涉及具体订单号的发货、支付或物流状态，调用 query_order 查询真实数据。
如果用户提到了工单号或者想知道之前提交的工单处理进度，调用 query_ticket 查询。
如果需要确认用户的身份、等级或者联系方式，调用 query_user 查询，用户 ID 通常需要先从对话里确认，不要凭空编造。
如果用户的问题属于退款政策、发货时效、账号安全这类通用规则性问题，调用 search_knowledge_base 检索相关说明，不要凭记忆直接回答政策类问题。
如果用户想确认某笔订单的支付方式、支付金额或支付时间，先通过用户自述或 query_ticket 返回结果拿到订单号，再调用 query_payment 查询真实流水，不要凭空猜测支付信息。
如果用户询问包裹运输进度、质疑物流为什么没有更新，先拿到订单号再调用 query_logistics 查询轨迹节点，结合轨迹时间判断是否真的延迟，不要凭感觉推测物流状态。查询结果是空时如实告知用户暂无物流记录，而不是编造一段轨迹。
以上工具可以在同一轮对话里按需要多次调用，不要凭空编造任何工具没有返回过的数据。

## 引用规范（重要）
当你使用知识库检索（search_knowledge_base）返回的片段来组织回答时，必须在回答中用 [数字] 标注每条关键信息的来源，数字对应片段列表中的序号。
例如，如果片段 1 来自售后政策文档、片段 2 来自退款规则文档，你的回答应该类似：

"根据售后政策，用户签收后 7 天内可申请无理由退款[1]，退款将在 3 个工作日内原路退回[2]。"

引用标注要紧跟被引用的那句话，不要把所有标注堆在段落末尾，也不要漏掉任何一条来自知识库的信息。如果某条信息是你自己的通用知识而非来自检索结果，不要给它加引用标注。

## 回答策略（根据用户意图调整）
系统会在每条用户消息之前注入意图识别结果，你需要根据意图类型调整回答策略：
- knowledge_qa：优先调用 search_knowledge_base 检索相关资料再回答，确保回答有依据。
- order_query：优先调用 query_order 获取订单数据，如果用户追问细节但没有提供订单号，先引导用户提供订单号。
- complaint_handle：先表达理解用户情绪，再调用相关工具核实情况，最后给出明确的处理方案和时间预期，不要只给一句"我们会尽快处理"。
- ticket_create：引导用户确认工单内容和期望的处理方式，确认后再调用 query_ticket 检查是否有重复工单。
- refund_advice：先调用 search_knowledge_base 查退款政策，如果用户提到了具体订单则同步调用 query_order 核实订单状态，结合政策和订单状态给出具体的退款建议。
- transfer_human：不要尝试挽留用户或继续追问，直接告知用户即将转接人工客服并说明后续流程。"""

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


async def stream_chat(session_id: str, message: str) -> AsyncGenerator[dict, None]:
    """处理一轮对话并把完整过程落库。

    时序是，用户消息先持久化，意图识别照旧前置，历史窗口由短期记忆从库里
    裁剪恢复，工具调用循环结束后把结构化回答连同意图、工具记录、引用来源
    写入消息表，再回填工单关联和自动标题，最后推送 session_meta 事件。
    """
    db = SessionLocal()
    try:
        repository = SessionRepository(db)
        memory = ConversationMemory(repository)

        session = repository.get_session(session_id)
        if session is None:
            # 路由层已拦过一次，这里防的是请求处理途中会话被并发删除
            yield {"type": "error", "message": f"会话 {session_id} 不存在或已被删除"}
            return
        thread_id = session.thread_id

        # 用户消息最先落库，后续任何模型调用失败，客服的提问都已经保住
        repository.append_message(
            session_id=session_id, thread_id=thread_id, role="user", content=message
        )
        repository.touch(session_id)

        # 意图识别，逻辑与 Day 11 一致，输入从"历史里最后一条 user"简化为入参 message
        intent_result: IntentResult | None = None
        if message.strip():
            try:
                intent_result = await classify_intent(message)
                if intent_result.confidence < _CONFIDENCE_THRESHOLD:
                    intent_result.need_human = True
            except Exception:
                intent_result = IntentResult(
                    intent="knowledge_qa",
                    confidence=0.0,
                    reasoning="意图识别调用失败，降级为通用知识问答模式",
                    need_human=False,
                )
            yield {
                "type": "intent",
                "data": {
                    "intent": intent_result.intent,
                    "confidence": intent_result.confidence,
                    "reasoning": intent_result.reasoning,
                    "need_human": intent_result.need_human,
                    "label": INTENT_LABELS.get(intent_result.intent, {}).get("label", ""),
                    "color": INTENT_LABELS.get(intent_result.intent, {}).get("color", ""),
                },
            }

        intent_hint = ""
        if intent_result:
            intent_label = INTENT_LABELS.get(intent_result.intent, {}).get(
                "label", intent_result.intent
            )
            intent_hint = (
                f"[系统提示] 本次对话的意图识别结果：{intent_label}"
                f"（置信度：{intent_result.confidence:.0%}）。判断依据：{intent_result.reasoning}"
            )
            if intent_result.need_human:
                intent_hint += " 注意：置信度较低，如果无法给出确定的回答，请主动建议用户转接人工客服。"

        # 历史窗口从数据库恢复并裁剪，刚落库的用户消息也在里面，不再手动追加
        context_messages = memory.load_context(thread_id)

        history: list[BaseMessage] = [
            SystemMessage(content=_AGENT_SYSTEM_PROMPT)]
        if intent_hint:
            history.append(SystemMessage(content=intent_hint))
        history.extend(context_messages)

        collected_sources: list[SourceInfo] = []
        collected_tool_calls: list[ToolCallResult] = []

        iteration = 0
        while iteration < _MAX_TOOL_ITERATIONS:
            iteration += 1
            ai_message = await _llm_with_tools.ainvoke(history)

            if not ai_message.tool_calls:
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
                history.append(
                    ToolMessage(
                        content=json.dumps(tool_result, ensure_ascii=False),
                        tool_call_id=tool_call["id"],
                    )
                )

                if tool_name == "search_knowledge_base" and isinstance(tool_result, dict):
                    for snippet in tool_result.get("snippets", []):
                        collected_sources.append(
                            SourceInfo(
                                index=snippet["index"],
                                filename=snippet["filename"],
                                chunk_index=snippet["chunk_index"],
                                content=snippet["content"],
                                score=snippet["score"],
                                page=snippet.get("page"),
                            )
                        )
        else:
            history.append(
                SystemMessage(content="已达到最大工具调用次数，请基于目前已有的信息直接给出结论。")
            )

        final_response: ChatResponse = await _structured_llm.ainvoke(history)
        final_response.tool_calls = collected_tool_calls
        yield {"type": "final", "data": final_response.model_dump()}

        if collected_sources:
            yield {
                "type": "sources",
                "data": {
                    # conversation_id 从今天起填真实的记忆线程 ID，前端可据此定位会话
                    "conversation_id": thread_id,
                    "sources": [source.model_dump() for source in collected_sources],
                },
            }

        # AI 回答连同完整链路信息落库，Day 12 详情页缺的"AI 分析结果"以后从这里取
        extra = {
            "intent": final_response.intent,
            "confidence": final_response.confidence,
            "need_human": final_response.need_human,
            "suggested_actions": final_response.suggested_actions,
            "tool_calls": [call.model_dump() for call in collected_tool_calls],
            "sources": [source.model_dump() for source in collected_sources],
            "task_intent": intent_result.model_dump() if intent_result else None,
        }
        repository.append_message(
            session_id=session_id,
            thread_id=thread_id,
            role="assistant",
            content=final_response.answer,
            extra=extra,
        )

        # Agent 成功查过工单就把会话关联到这张工单，供工单详情页反查处理过程
        linked_ticket_no = session.ticket_no
        if not linked_ticket_no:
            for call in collected_tool_calls:
                if (
                    call.name == "query_ticket"
                    and isinstance(call.result, dict)
                    and "error" not in call.result
                ):
                    linked_ticket_no = str(call.args.get("ticket_no") or "")
                    break
        if linked_ticket_no and linked_ticket_no != session.ticket_no:
            repository.link_ticket(session_id, linked_ticket_no)

        # 首轮对话结束后生成标题，任何失败都退化为首条消息截断，不影响主链路
        latest_title = session.title
        if session.title == "新会话":
            try:
                latest_title = await generate_title(message)
            except Exception:
                latest_title = message.strip()[:12] or "新会话"
            repository.update_title(session_id, latest_title)

        repository.touch(session_id)
        yield {
            "type": "session_meta",
            "data": {
                "session_id": session_id,
                "title": latest_title,
                "ticket_no": linked_ticket_no,
            },
        }
    except Exception as exc:
        # 用户消息已经落库，这里只保证错误能以事件形式到达前端，不追加伪造的 AI 消息
        yield {"type": "error", "message": str(exc)}
    finally:
        db.close()
