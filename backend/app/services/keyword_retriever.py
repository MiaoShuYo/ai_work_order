from langchain_community.retrievers import BM25Retriever
from app.services.retriever import get_all_chunks

# 模块加载时从 Chroma 全量读取文档构建 BM25 索引，之后复用，不每次查询重建。默认的 preprocess_func 是 str.split，对中文分词效果一般，但 BM25 本身依赖的是词频统计，即使没有专门的中文分词器，在文档语料足够大时仍然能通过字符级的 n-gram 匹配捕捉到一定相关性，加上向量检索兜底，这里的 BM25 更多是作为关键词命中能力的补充而非主力检索手段。
_bm25_retriever: BM25Retriever | None = None


def _get_bm25() -> BM25Retriever:
    global _bm25_retriever
    if _bm25_retriever is not None:
        return _bm25_retriever
    chunks = get_all_chunks()
    if not chunks:
        # 知识库为空时返回一个空 retriever，keyword_search 里会判断并返回空列表
        _bm25_retriever = BM25Retriever.from_documents([])
    else:
        _bm25_retriever = BM25Retriever.from_documents(chunks)
    return _bm25_retriever


def keyword_search(query: str, top_k: int = 5) -> list[dict]:
    """
    用 BM25 关键词匹配在知识库中检索，返回结构对齐 retriever.retrieve 的格式。如果知识库尚未索引任何文档，返回空列表。
    """
    bm25 = _get_bm25()
    bm25.k = top_k
    docs = bm25.invoke(query)
    return [
        {
            "content": doc.page_content,
            # BM25 返回的分数没有固定范围，这里用原始分数，前端展示时做相对比较，不做归一化是因为归一化会掩盖"这条片段和其他片段的差距到底有多大"这个信息，在调试场景下保留原始分数对判断关键词命中的强度更有帮助。
            "score": round(doc.metadata.get("score", 0.0), 4),
            "document_id": doc.metadata.get("document_id", ""),
            "filename": doc.metadata.get("filename", ""),
            "chunk_index": doc.metadata.get("chunk_index", 0),
        }
        for doc in docs
    ]
