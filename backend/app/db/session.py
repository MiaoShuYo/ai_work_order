import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 数据库文件路径通过环境变量配置，默认落在项目根目录下的app.db，Day 20 部署时只需要把这个环境变量换成 PostgreSQL 的连接字符串，上层 SessionLocal 用法不用改
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# SQLite 默认要求同一个连接只能在创建它的线程里使用，但 FastAPI 处理请求时会用到线程池，check_same_thread=False 关掉这个限制，这是 SQLite 开发环境下的常规做法，换成 PostgreSQL 之后这个参数就不需要了。
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith(
    "sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    FastAPI 依赖注入用的会话生成器，请求处理完毕后无论成功还是抛出异常都会关闭会话。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
