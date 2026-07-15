from pydantic import BaseModel, Field
from typing import Optional


class KnowledgeSnippet(BaseModel):
    """
    知识库命中的一条片段，index 是本次检索中的序号，供 LLM 在回答中引用。
    """
    content: str = Field(description="片段的正文内容")
    score: float = Field(description="相似度分数，0 到 1 之间，越高越相关")
    document_id: str = Field(description="来源文档的 ID，可追溯到 documents 表")
    filename: str = Field(description="来源文档的文件名，用于前端展示")
    chunk_index: int = Field(description="片段在文档中的序号，从 0 开始")
    index: int = Field(default=0, description="在被刺检索结果中的序号，从 1 开始")


class SourceInfo(BaseModel):
    """
    单条引用来源，返回给前端用于渲染引用列表和原文抽屉。
    和 KnowledgeSnippet 的区别：SourceInfo 面向展示层，去掉了 document_id 和 score 的原始精度，
    增加了可选的 page 字段用于 PDF 类文档的页码展示。
    """
    index: int = Field(description="引用序号，对应回答中的 [数字] 标注")
    filename: str = Field(description="来源文档的文件名")
    chunk_index: int = Field(description="片段在文档中的序号")
    content: str = Field(description="片段原文，供前端抽屉展开查看")
    score: float = Field(description="相似度分数，百分比展示用")
    page: Optional[int] = Field(
        default=None, description="PDF 文档的页码，非 PDF 文件为 None")
