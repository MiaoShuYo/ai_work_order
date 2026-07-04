from dotenv import load_dotenv

# load_dotenv 必须在任何导入自己模块（如 llm_client）之前运行，
# 因为 llm_client 在模块加载时就会读取环境变量来初始化 ChatOpenAI。
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.chat import router as chat_router
import uvicorn

app = FastAPI(title="AI 只是工单助手")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
