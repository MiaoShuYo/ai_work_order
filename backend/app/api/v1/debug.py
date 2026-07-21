import time
from typing import Optional

from fastapi import APIRouter
from langchain_classic.retrievers import EnsembleRetriever

from app.schemas.debug import DebugRetrievalRequest, DebugSnippet, DebugRetrievalResponse, StrategyResult
from app.services.keyword_retriever import keyword_search, _get_bm25
from app.services.reranker import rerank
from app.services.retriever import as_retriever, retrieve, get_all_chunks

router = APIRouter(prefix="/api/v1/rag", tags=["rag-debug"])

# 上下文预览的包装模板，模拟 Day 9 的系统提示词中知识库部分的结构，实际送入 LLM 时系统提示词还会包含工具使用规范、引用规范等内容，这里只拼接与检索直接相关的片段部分，让调试者看到"模型看到的知识库内容是什么"。
_CONTEXT_TEMPLATE = """以下是从公司知识库中检索到的相关文档片段，请基于这些片段回答用户的问题：

{chunks}

---
用户问题：{query}
请基于以上知识库片段给出回答，并在回答中用 [数字] 标注每条关键信息的来源。"""


def _build_context_preview(query: str, snippets: list[DebugSnippet]) -> str:
    """
    将检索到的片段拼成一段模拟的 LLM 上下文，方便调试者直接复制去手动测试模型效果。
    """
    chunks_text = "\n\n---\n\n".join(
        f"[{i+1}]（来源：{s.filename}，片段 #{s.chunk_index+1}，分数：{s.score}）\n{s.content}" for i, s in enumerate(snippets)
    )
    return _CONTEXT_TEMPLATE.format(chunks=chunks_text, query=query)


def _run_vector(query: str, top_k: int) -> tuple[list[DebugSnippet], float]:
    start = time.perf_counter()
    results = retrieve(query, top_k)
    elapsed = (time.perf_counter() - start) * 1000
    snippets = [
        DebugSnippet(strategy="vector", **r) for r in results
    ]
    return snippets, elapsed


def _run_keyword(query: str, top_k: int) -> tuple[list[DebugSnippet], float]:
    start = time.perf_counter()
    results = keyword_search(query, top_k)
    elapsed = (time.perf_counter() - start) * 1000
    snippets = [
        DebugSnippet(strategy="keyword", **r) for r in results
    ]
    return snippets, elapsed


def _run_hybrid(query: str, top_k: int) -> tuple[list[DebugSnippet], float]:
    start = time.perf_counter()
    all_chunks = get_all_chunks()
    if not all_chunks:
        return [], (time.perf_counter() - start) * 1000

    dense = as_retriever(top_k)
    sparse = _get_bm25()
    sparse.k = top_k

    ensemble = EnsembleRetriever(
        retrievers=[dense, sparse], weights=[0.6, 0.4], c=60)
    docs = ensemble.invoke(query)

    elapsed = (time.perf_counter() - start) * 1000
    snippets = [
        DebugSnippet(
            strategy="hybrid",
            content=doc.page_content,
            # EnsembleRetriever 在做 RRF 融合后不会保留原始分数，metadata 里也没有 score，这里统一给 0.0，前端展示时可以提示"混合检索不提供逐条分数"。
            score=0.0,
            filename=doc.metadata.get("filename", ""),
            chunk_index=doc.metadata.get("chunk_index", 0),
        )
        for doc in docs
    ]
    return snippets, elapsed


_STRATEGY_RUNNERS = {
    "vector": _run_vector,
    "keyword": _run_keyword,
    "hybrid": _run_hybrid,
}


@router.post("/debug", response_model=DebugRetrievalResponse)
def debug_retrieval(req: DebugRetrievalRequest):
    """
    检索调试接口，按请求中指定的 strategies 并行执行多种检索策略并返回对比结果。
    """
    results: list[StrategyResult] = []

    for strategy in req.strategies:
        runner = _STRATEGY_RUNNERS.get(strategy)
        if runner is None:
            continue

        snippets, elapsed = runner(req.query, req.top_k)

        if req.enable_rerank and snippets:
            # 重排序需要 dict 格式，先把 DebugSnippet 转成 dict
            snippet_dicts = [s.model_dump() for s in snippets]
            reranked_dicts = rerank(req.query, snippet_dicts, req.top_k)
            snippets = [DebugSnippet(**d) for d in reranked_dicts]
            # 重排后更新策略名，方便前端区分"混合检索"和"混合检索+重排"
            snippets = [
                DebugSnippet(
                    strategy=f"{strategy}+rerank",
                    content=s.content,
                    score=s.score,
                    filename=s.filename,
                    chunk_index=s.chunk_index,
                )
                for s in snippets
            ]

        results.append(
            StrategyResult(
                strategy=strategy,
                snippets=snippets,
                context_preview=_build_context_preview(req.query, snippets),
                elapsed_ms=round(elapsed, 1),
            )
        )

    return DebugRetrievalResponse(query=req.query, results=results)
