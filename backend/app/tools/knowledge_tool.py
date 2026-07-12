from langchain_core.tools import tool
from app.schemas.knowledge import KnowledgeSnippet
from app.services.retriever import retrieve


@tool
def search_knowledge_base(query: str) -> dict:
    """
    在知识库里检索与 query 语义相关的文档片段，query 是从用户问题里提炼出的自然语言查询，不需要手动拆成关键词，向量检索会自动处理语义相似度，本次检索最多返回 5 条片段。
    """
    results = retrieve(query)
    if not results:
        return {
            "snippets": [],
            "message": "未在知识库中找到相关内容，建议尝试换一种问法或者联系人工客服。"
        }
    return {
        "snippets": [KnowledgeSnippet(**item).model_dump() for item in results]
    }
