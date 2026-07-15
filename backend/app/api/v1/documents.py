import os
import uuid

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.document_repository import add_document, list_documents, get_document, update_status
from app.schemas.document import DocumentInfo
from app.services.document_parser import parse_document

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

_STORAGE_DIR = "storage/documents"
os.makedirs(_STORAGE_DIR, exist_ok=True)


def _to_document_info(document) -> DocumentInfo:
    return DocumentInfo(
        id=document.id,
        filename=document.filename,
        file_type=document.file_type,
        status=document.status,
        size=document.size,
        uploaded_at=document.uploaded_at,
        summary=document.summary,
        error=document.error,
    )


@router.post("", response_model=DocumentInfo)
async def upload_document(file: UploadFile, db: Session = Depends(get_db)) -> DocumentInfo:
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

    try:
        summary = parse_document(file_path, file_type)
        update_status(db, doc_id, status="已完成", summary=summary)
        document.status = "已完成"
        document.summary = summary
    except Exception as e:
        # 解析失败不让这次请求以 500 收场，而是把文档状态标记为失败，管理员在列表页就能直接看到失败原因，不需要去翻后端日志。
        update_status(db, doc_id, status="失败", error=str(e))
        document.status = "失败"
        document.error = str(e)

    return _to_document_info(document)

@router.get("", response_model=list[DocumentInfo])
def list_documents_endpoint(db: Session = Depends(get_db)) -> list[DocumentInfo]:
    return [_to_document_info(doc) for doc in list_documents(db)]
