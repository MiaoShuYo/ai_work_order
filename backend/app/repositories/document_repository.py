from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.document import DocumentModel


def add_document(db: Session, doc_id: str, filename: str, file_type: str, file_path: str, size: int) -> DocumentModel:
    """
    插入一条状态为解析中的文档记录，chunk_count 先记 0，摘要和错误信息此时都还是空的。
    """
    document = DocumentModel(
        id=doc_id,
        filename=filename,
        file_type=file_type,
        file_path=file_path,
        size=size,
        status="解析中",
        chunk_count=0,
        uploaded_at=datetime.now(timezone.utc)
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def get_document(db: Session, doc_id: str) -> Optional[DocumentModel]:
    return db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()


def list_documents(db: Session) -> list[DocumentModel]:
    return db.query(DocumentModel).order_by(DocumentModel.uploaded_at.desc()).all()


def update_status(db: Session, doc_id: str, status: str, summary: Optional[str] = None, error: Optional[str] = None, chunk_count: Optional[int] = None) -> None:
    """
    更新文档的处理状态，summary、error、chunk_count 只在调用方明确传入时才写入，今天一份文档要经历四五次状态推进，不这么改的话后面的调用会把前面已经写好的值冲掉。
    """
    document = get_document(db, doc_id)
    if document is None:
        return
    document.status = status
    if summary is not None:
        document.summary = summary
    if error is not None:
        document.error = error
    if chunk_count is not None:
        document.chunk_count = chunk_count
    db.commit()
