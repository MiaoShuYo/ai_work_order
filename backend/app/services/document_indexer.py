import os
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

_CHUNK_SIZE = 500
_CHUNK_VOERLAP = 50

_VECTOR_STORE_DIR = "backend/storage/vector_store"
os.makedirs(_VECTOR_STORE_DIR, exist_ok=True)

# 和 llm_client.py 里的 ChatOpenAI 一样走 OpenAI 协议兼容接口，复用同一套 API Key 和 base_url，换供应商时不需要单独维护一份 Embedding 凭证。
_embeddings = OpenAIEmbeddings(
    model=os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-m3"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE_URL") or None
)

# 所有文档共用一个 collection，检索时靠 metadata 里的 document_id 区分来源，persist_directory 指定之后 Chroma 会在写入时自动落盘，不需要再手动调用 persist。
_vector_store = Chroma(
    collection_name="documents",
    embedding_function=_embeddings,
    persist_directory=_VECTOR_STORE_DIR
)

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=_CHUNK_SIZE,
    chunk_overlap=_CHUNK_VOERLAP)


def split_text(text: str) -> list[str]:
    """
    把一段长文本切成多个片段，chunk_overlap 保留一部分重叠内容，避免语义在切分边界被硬生生截断。今天的 chunk_size 按字符数计算，不是按 token 数，对中文资料够用，后续如果要精细控制模型的
    上下文占用，可以换成基于 tiktoken 编码器的切片方式。
    """
    return _splitter.split_text(text)


def index_chunks(doc_id: str, filename: str, chunks: list[str]) -> None:
    """
    把切好的片段向量化并写入 Chroma，metadata 里记录 document_id 和片段序号，后面要重新索引或者删除这份文档的片段时，可以按 document_id 过滤定位。
    """
    documents = [
        Document(
            page_content=chunk,
            metadata={
                "document_id": doc_id,
                "chunk_index": i,
                "filename": filename
            }
        )
        for i, chunk in enumerate(chunks)
    ]
    ids = [f"{doc_id}-{i}" for i in range(len(chunks))]
    _vector_store.add_documents(documents, ids=ids)
