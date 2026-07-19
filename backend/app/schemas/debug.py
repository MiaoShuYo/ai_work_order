from pydantic import BaseModel, Field


class DebugRetrievalRequest(BaseModel):
    """
    检索调试请求，strategies 支持 vector / keyword / hybrid 三种，可多选，勾选多种策略时接口会并行执行并在响应中分别返回各自的结果。   
    """

    query: str = Field(min_length=1, description="检索查询文本")
    top_k: int = Field(default=5, ge=1, le=20, description="返回的片段数量上限")
    strategies: list[str] = Field(
        default=["vector", "keyword", "hybrid"],
        description="要对比的检索策略列表，可选值：vector / keyword / hybrid",
    )
    enable_rerank: bool = Field(
        default=False, description="是否在检索后对候选片段做 cross-encoder 重排序")


class DebugSnippet(BaseModel):
    """
    单条检索片段的调试视图，比 KnowledgeSnippet 多一个 strategy 字段标记来源策略。
    """

    content: str = Field(description="片段正文")
    score: float = Field(description="相似度分数，不同策略的分数含义不同，不宜直接跨策略比较数值大小")
    filename: str = Field(description="来源文档的文件名")
    chunk_index: int = Field(description="片段在文档中的序号")
    strategy: str = Field(description="产生这条片段的检索策略名称")


class StrategyResult(BaseModel):
    """
    单种策略的完整检索结果。
    """

    strategy: str = Field(description="策略名称，如 vector / keyword / hybrid")
    snippets: list[DebugSnippet] = Field(description="检索到的片段列表")
    context_preview: str = Field(description="将所有片段按顺序拼接后的上下文预览，模拟送入 LLM 前的形态")
    elapsed_ms: float = Field(description="检索耗时，单位毫秒")

class DebugRetrievalResponse(BaseModel):
    """
    检索调试接口的完整响应，包含请求的查询文本和所有策略的对比结果。
    """

    query: str = Field(description="原始查询文本，方便前端回显")
    results: list[StrategyResult] = Field(description="各策略的检索结果列表，顺序对应请求中的 strategies")