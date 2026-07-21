from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class DocumentInfo(BaseModel):
    """
    文档信息，status 用 Literal 限定取值范围，今天在 Day 6 的处理中、已完成、失败之上，拆成解析中、切片完成、向量化中、可检索、失败五个更贴近真实处理流程的阶段。
    """
    id: str = Field(description="文档 ID")
    filename: str = Field(description="原始文件名")
    file_type: str = Field(description="文件扩展名，如 pdf、docx、xlsx、csv、md")
    status: Literal["解析中", "切片完成", "向量化中", "可检索",
                    "失败", "已完成"] = Field(description="文档处理状态")
    size: int = Field(description="文件大小，单位字节")
    chunk_count: int = Field(default=0, description="切片数量，切片完成之前恒为 0")
    uploaded_at: datetime = Field(description="上传时间")
    summary: Optional[str] = Field(default=None, description="解析出的文本摘要")
    error: Optional[str] = Field(default=None, description="解析失败时的错误信息")


class DocumentLogEntry(BaseModel):
    """
    处理日志条目，对应 document_logs 表的一行，按时间正序返回给前端。
    """

    id: int = Field(description="日志 ID")
    step: str = Field(description="处理步骤，如解析、切片、向量化")
    message: str = Field(description="这一步的详细说明")
    created_at: datetime = Field(description="记录时间")
