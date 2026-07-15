import os
import uuid

from fastapi import APIRouter, Depends, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.document_log_repository import list_logs
from app.repositories.document_repository import add_document, list_documents
from app.schemas.document import DocumentInfo, DocumentLogEntry
from app.models.document import DocumentModel
from app.services.document_pipeline import process_document

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

_STORAGE_DIR = "backend/storage/documents"
os.makedirs(_STORAGE_DIR, exist_ok=True)


def _to_document_info(document: DocumentModel) -> DocumentInfo:
    return DocumentInfo(
        id=document.id,
        filename=document.filename,
        file_type=document.file_type,
        status=document.status,
        size=document.size,
        chunk_count=document.chunk_count,
        uploaded_at=document.uploaded_at,
        summary=document.summary,
        error=document.error,
    )


@router.post("", response_model=DocumentInfo)
async def upload_document(file: UploadFile, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> DocumentInfo:
    doc_id = str(uuid.uuid4())
    file_type = (file.filename.rsplit(".", 1)
                 [-1] if "." in file.filename else "").lower()

    # 用文档 ID 而不是原始文件名拼接磁盘路径，避免用户上传的文件名里带路径穿越字符，导致文件被写到 storage 目录之外的位置。
    file_path = os.path.join(_STORAGE_DIR, f"{doc_id}.{file_type}")

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    document = add_document(db, doc_id=doc_id, filename=file.filename,
                            file_type=file_type, file_path=file_path, size=len(content))
    # 解析、切片、向量化挪到后台任务里执行，这里保存完文件、插完一条解析中的记录就立刻返回，不再等文档处理完，避免大文件解析时把这次 HTTP 请求挂起太久。
    background_tasks.add_task(process_document, doc_id,
                              file_path, file_type, file.filename)

    return _to_document_info(document)


@router.get("", response_model=list[DocumentInfo])
def list_documents_endpoint(db: Session = Depends(get_db)) -> list[DocumentInfo]:
    return [_to_document_info(doc) for doc in list_documents(db)]


@router.get("/{doc_id}/logs", response_model=list[DocumentLogEntry])
def list_document_logs(doc_id: str, db: Session = Depends(get_db)) -> list[DocumentLogEntry]:
    return [
        DocumentLogEntry(id=log.id, step=log.step, message=log.message, created_at=log.created_at) for log in list_logs(db, doc_id)
    ]