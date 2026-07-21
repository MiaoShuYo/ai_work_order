import os
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

_VECTOR_STORE_DIR = "backend/storage/vector_store"

# Embedding 配置和 document_indexer.py 保持一致，模型名、API Key、base_url 都走同一套环境变量，换模型供应商时改一处就行。
_embeddings = OpenAIEmbeddings(
    model=os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-m3"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL") or None,
)

_vector_store = Chroma(
    collection_name="documents",
    embedding_function=_embeddings,
    persist_directory=_VECTOR_STORE_DIR
)


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """
    在知识库中检索与 query 语义最接近的 top_k 个文档片段，返回的每个 dict 包含正文内容、归一化后的相似度分数（0 到 1，越高越相关）和来源文档的元信息。
    """
    results = _vector_store.similarity_search_with_score(query, k=top_k)
    return [
        {
            "content": doc.page_content,
            # Chroma 返回的是距离（余弦距离默认范围 0~2），1 - 距离/2 映射到 0~1 区间，
            # 再用 max/min 兜底，防止极端情况下分数溢出这个区间。
            "score": round(max(0.0, min(1.0, 1.0 - score / 2)), 4),
            "document_id": doc.metadata.get("document_id", ""),
            "filename": doc.metadata.get("filename", ""),
            "chunk_index": doc.metadata.get("chunk_index", 0),
        }
        for doc, score in results
    ]


def get_all_chunks() -> list[Document]:
    """
    从 Chroma 中获取全部已索引的文档片段，返回 LangChain Document 列表。Chroma.get() 在不传 limit 时默认返回 collection 中的全部文档，包含 page_content 和 metadata，
    这个函数供 BM25 关键词检索构建索引时使用，也供调试页面直接查看全量语料。
    """
    result = _vector_store.get()
    if not result or not result["documents"]:
        return []
    return [
        Document(
            page_content=text,
            metadata={
                "document_id": result["metadatas"][i].get("document_id", ""),
                "filename": result["metadatas"][i].get("filename", ""),
                "chunk_index": result["metadatas"][i].get("chunk_index", 0),
            },
        )
        for i, text in enumerate(result["documents"])
    ]


def as_retriever(top_k: int = 5):
    """
    返回 LangChain 兼容的 BaseRetriever，供 EnsembleRetriever 做 RRF 融合时使用。这里只包一层 search_kwargs，不做额外的分数归一化，RRF 算法本身用排名而非原始分数做融合，所以分数是余弦距离还是相似度对融合结果没有影响。
    """
    return _vector_store.as_retriever(search_kwargs={"k": top_k})
