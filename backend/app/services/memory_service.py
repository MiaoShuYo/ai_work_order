import os
from app.repositories.session_repository import SessionRepository

# 进模型上下文窗口的最大消息条数，对话超过这个长度后最早的消息不再进入上下文，
# 但仍然完整保留在消息表里，会话恢复不受影响。线上按真实 token 用量调整这个值。
_MAX_HISTORY_MESSAGES = int(os.getenv("CHAT_MAX_HISTORY_MESSAGES"), "20")


class ConversationMemory:
    """
    短期记忆，决定每一轮对话把哪些历史消息放进模型的上下文窗口。
    持久化和全量查询归 SessionRepository 管，这里只做窗口裁剪，以后换成 token 预算裁剪或历史摘要时，只改这一个类。
    """

    def __init__(self, repository: SessionRepository):
        self.repository = repository

    def load_context(self, thread_id: str, limit: int = _MAX_HISTORY_MESSAGES) -> list[dict[str, str]]:
        rows = self.repository.list_context_messages(thread_id, limit)
        # 只带 role 和 content 两个键，工具调用记录和引用不进下一轮上下文，它们已经被当轮 AI 回答消化过，且工具结果有时效性。
        return [{"role": row.role, "content": row.content} for row in rows]
