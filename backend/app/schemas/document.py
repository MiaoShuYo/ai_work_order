from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class DocumentInfo(BaseModel):
    """
    文档信息，status 用 Literal 限定取值范围，避免非法状态流到前端。
    """
    id: str = Field(description="文档 ID")
    filename: str = Field(description="原始文件名")
    file_type: str = Field(description="文件扩展名，如 pdf、docx、xlsx、csv、md")
    status: Literal["处理中", "已完成", "失败"] = Field(description="文档处理状态")
    size: int = Field(description="文件大小，单位字节")
    uploaded_at: datetime = Field(description="上传时间")
    summary: Optional[str] = Field(default=None, description="解析出的文本摘要")
    error: Optional[str] = Field(default=None, description="解析失败时的错误信息")
