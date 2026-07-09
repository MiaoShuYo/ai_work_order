from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.document import DocumentModel


def add_document(db: Session, doc_id: str, filename: str, file_type: str, file_path: str, size: int) -> DocumentModel:
    """
    插入一条状态为处理中的文档记录，摘要和错误信息此时都还是空的。
    """
    document = DocumentModel(
        id=doc_id,
        filename=filename,
        file_type=file_type,
        file_path=file_path,
        size=size,
        status="处理中",
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


def update_status(db: Session, doc_id: str, status: str, summary: Optional[str] = None, error: Optional[str] = None) -> None:
    """
    更新文档的处理状态，解析成功传 summary，解析失败传 error，两者不会同时出现。
    """
    document = get_document(db, doc_id)
    if document is None:
        return
    document.status = status
    document.summary = summary
    document.error = error
    db.commit()
