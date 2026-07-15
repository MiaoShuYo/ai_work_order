from langchain_core.tools import tool
from app.schemas.knowledge import KnowledgeSnippet
from app.services.retriever import retrieve


@tool
def search_knowledge_base(query: str) -> dict:
    """
    在知识库里检索与 query 语义相关的文档片段，返回的每条片段都带有 index 序号，模型在回答中引用具体片段时，必须使用 [index] 格式标注来源，例如 [1]、[2]。query 是从用户问题里提炼出的自然语言查询，不需要手动拆成关键词。
    """
    results = retrieve(query)
    if not results:
        return {
            "snippets": [],
            "message": "未在知识库中找到相关内容，建议尝试换一种问法或者联系人工客服。"
        }
    snippets = []
    for i, item in enumerate(results):
        item["index"] = i+1
        snippets.append(KnowledgeSnippet(**item).model_dump())
    return {"snippets": snippets}
