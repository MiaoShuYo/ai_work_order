from pydantic import BaseModel, Field


class KnowledgeSnippet(BaseModel):
    """
    知识库命中的一条片段，字段对齐 retriever.retrieve 的返回结构。score 是归一化后的相似度，范围 0 到 1，越高说明和查询越相关。
    """
    content: str = Field(description="片段的正文内容")
    score: float = Field(description="相似度分数，0 到 1 之间，越高越相关")
    document_id: str = Field(description="来源文档的 ID，可追溯到 documents 表")
    filename: str = Field(description="来源文档的文件名，用于前端展示")
    chunk_index: int = Field(description="片段在文档中的序号，从 0 开始")
