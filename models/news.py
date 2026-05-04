from datetime import datetime
from email.policy import default
from sqlalchemy import Index

from sqlalchemy import Text, TIMESTAMP, ForeignKey
from sqlalchemy import DateTime, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapper, mapped_column
from sqlalchemy.sql.functions import func


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )


class Category(Base):
    __tablename__ = "news_category"
    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, comment="分类ID"
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="分类名称")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="分类排序")

    def __repr__(self):
        return f"<Category(id='{self.id}',name='{self.name}',sort_order='{self.sort_order}')>"


class News(Base):
    __tablename__ = "news"

    # 索引
    __table_args__ = (
        Index("ix_news_publish_time", "publish_time"),
        Index("ix_news_category_id", "category_id"),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="新闻ID"
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="新闻标题")

    description: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="新闻简介"
    )

    content: Mapped[str] = mapped_column(Text, nullable=False, comment="新闻内容")

    image: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="封面图片URL"
    )

    author: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="作者"
    )

    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("news_category.id"),
        nullable=False,
        index=True,
        comment="分类ID",
    )

    views: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="浏览量"
    )

    publish_time: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False, comment="发布时间"
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False, comment="创建时间"
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间",
    )

    def __repr__(self):
        return f"News(id={self.id}, title={self.title!r})"
