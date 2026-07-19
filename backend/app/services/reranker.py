from typing import Optional
from flashrank import Ranker, RerankRequest

# FlashRank 默认使用 ms-marco-MiniLM-L6-v2 模型，第一次加载时从 HuggingFace 下载模型文件，模型大小约 100MB，加载后缓存在内存中，后续查询不再有 IO 开销。
_ranker: Optional[Ranker] = None


def _get_ranker() -> Ranker:
    global _ranker
    if _ranker is None:
        _ranker = Ranker()
    return _ranker


def rerank(query: str, documents: list[dict], top_k: int = 5) -> list[dict]:
    """
    用 cross-encoder 对候选片段重排序，documents 的每个 dict 必须包含 content 字段，返回按新分数降序排列的片段列表，保留原始 metadata 字段不变。如果候选片段数不超过 top_k，不执行重排序，直接原样返回。
    """
    if len(documents) <= top_k:
        return documents

    ranker = _get_ranker()
    passages = [{
        "text": doc["content"], "metadata": doc
    } for doc in documents]
    request = RerankRequest(query=query, passages=passages)
    results = ranker.rerank(request)
    reranked = []
    for r in results[:top_k]:
        original = r["metadata"]
        original["score"] = round(r["score"], 4)
        reranked.append(original)
    return reranked
