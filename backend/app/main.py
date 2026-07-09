from app.db.seed import seed_initial_data
from app.db.session import SessionLocal
import uvicorn
from app.api.v1.chat import router as chat_router
from app.api.v1.documents import router as documents_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# load_dotenv 必须在任何导入自己模块（如 llm_client）之前运行，
# 因为 llm_client 在模块加载时就会读取环境变量来初始化 ChatOpenAI。
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()
    yield


app = FastAPI(title="AI 只是工单助手", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1")
app.include_router(documents_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
