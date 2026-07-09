from sqlalchemy import Column, String

from app.db.base import Base


class UserModel(Base):
    """
    用户表，字段对应 schemas/user.py 里的 UserInfo。
    """
    __tablename__ = "users"
    user_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    level = Column(String, nullable=False)
    phone = Column(String, nullable=False)
