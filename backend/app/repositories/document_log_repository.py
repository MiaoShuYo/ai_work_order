from sqlalchemy.orm import Session
from app.models.document_log import DocumentLogModel


def add_log(db: Session, doc_id: str, step: str, message: str) -> None:
    """
    追加一条处理日志，不做去重和合并，每一步的详细记录都完整保留，方便排查卡在了哪一步。
    """
    db.add(DocumentLogModel(document_id=doc_id, step=step, message=message))
    db.commit()


def list_logs(db: Session, doc_id: str) -> list[DocumentLogModel]:
    return (
        db.query(DocumentLogModel)
        .filter(DocumentLogModel.document_id == doc_id)
        .order_by(DocumentLogModel.created_at.asc())
        .all()
    )
