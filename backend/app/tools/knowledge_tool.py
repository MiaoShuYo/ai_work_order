from langchain_core.tools import tool
from app.schemas.knowledge import KnowledgeSnippet

# 今天先用几条写死的文档模拟知识库，验证“判断需要查资料、调用检索、组织回答”这条链路，第 2 周接入向量库之后，只需要替换这个列表和下面的匹配逻辑，search_knowledge_base 对外的签名不变。
_MOCK_DOCS: list[KnowledgeSnippet] = [
    KnowledgeSnippet(
        title="退款政策说明",
        content="订单支付成功后 7 天内且尚未发货的，可以申请无理由退款，退款会在 3 个工作日内原路退回。",
        source="knowledge_base/refund_policy.md",
    ),
    KnowledgeSnippet(
        title="发货时效说明",
        content="普通商品在支付成功后 48 小时内安排发货，偏远地区可能延长至 72 小时。",
        source="knowledge_base/shipping_sla.md",
    ),
    KnowledgeSnippet(
        title="账号安全说明",
        content="连续输错密码 5 次会临时锁定账号 30 分钟，可以通过绑定手机号验证码解锁。",
        source="knowledge_base/account_security.md",
    ),
]


@tool
def search_knowledge_base(query: str) -> dict:
    """
    按关键词再知识库里检索相关说明，query 是从用户问题里提炼出来的关键词，比如退款、发货时效、账号锁定，今天的实现只是简单的关键此包含匹配，不支持语义相似的问法。
    """
    hits = [doc for doc in _MOCK_DOCS if query in doc.content or query in doc.title]
    return {"snippets": [hit.model_dump() for hit in hits]}
