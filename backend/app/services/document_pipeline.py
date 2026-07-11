from app.db.session import SessionLocal
from app.repositories.document_log_repository import add_log
from app.repositories.document_repository import update_status
from app.services.document_indexer import split_text, index_chunks
from app.services.document_parser import parse_document

_SUMMARY_MAX_LENGTH = 500


def process_document(doc_id: str, file_path: str, file_type: str, filename: str) -> None:
    """
    文档处理的完整流水线，解析、切片、向量化，每一步都更新状态并写一条日志。这个函数跑在 BackgroundTasks 里，执行时机在 HTTP 响应发出之后，不在请求的依赖注入生命周期内，不能像路由函数那样通过 Depends(get_db) 拿会话，要像 Day 6 的工具函数一样自己开、自己关会话。
    """
    db = SessionLocal()
    try:
        try:
            full_text = parse_document(file_path, file_type)
        except Exception as e:
            update_status(db, doc_id, status="失败", error=str(e))
            add_log(db, doc_id, step="解析", message=f"解析失败：{str(e)}")
            return
        summary = full_text[:_SUMMARY_MAX_LENGTH]
        add_log(db, doc_id, step="解析", message=f"解析完成，正文长度{len(full_text)} 字符")

        try:
            chunks = split_text(full_text)
        except Exception as e:
            update_status(db, doc_id, status="失败",
                          erro=str(e), summary=summary)
            add_log(db, doc_id, step="切片", message=f"切片失败：{str(e)}")
            return

        update_status(db, doc_id, status="切片完成",
                      summary=summary, chunk_count=len(chunks))
        add_log(db, doc_id, step="切片", message=f"切片完成，共 {len(chunks)} 个片段")

        update_status(db, doc_id, status="向量化中")
        add_log(db, doc_id, step="向量化", message="开始调用向量模型")

        try:
            index_chunks(doc_id, filename, chunks)
        except Exception as exc:
            update_status(db, doc_id, status="失败", error=str(exc))
            add_log(db, doc_id, Step="向量化", message=f"向量化失败：{exc}")
            return
        
        update_status(db,doc_id,status="可检索")
        add_log(db,doc_id,step="向量化",message="向量化完成，已写入索引，可以被检索")
    finally:
        db.close()
