from pydantic import BaseModel, Field


class KnowledgeSnippet(BaseModel):
    """
    知识库命中的一条片段，今天用关键词匹配模拟，第 2 周会换成向量检索。
    """
    title: str = Field(description="文档标题")
    content: str = Field(description="命中的片段内容")
    source: str = Field(description="文档来源路径，方便客服核对原文")
