from datetime import datetime
from sqlalchemy import DateTime, Index, ForeignKey
from sqlalchemy import String, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from typing import Optional


class Base(DeclarativeBase):
    pass


class User(Base):

    __tablename__ = "user"

    __table_args__ = (
        Index("idx_username", "username"),
        Index("phone_idx", "phone"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    nickname: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    gender: Mapped[str] = mapped_column(
        Enum("male", "female", "unknown"), default="unknown", nullable=False
    )

    bio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    def __repr__(self):
        return f"User(id={self.id}, username={self.username!r})"


class UserToken(Base):
    __tablename__ = "user_token"

    __table_args__ = (
        Index("idx_token", "token"),
        Index("user_id_idx", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False, comment="用户ID"
    )

    token: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, comment="登录令牌"
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="过期时间"
    )

    def __repr__(self):
        return f"UserToken(id={self.id}, token={self.token!r}, user_id={self.user_id})"
