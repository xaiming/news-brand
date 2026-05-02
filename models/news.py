from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from config.db_conf import Base
import datetime


class NewsCategory(Base):
    __tablename__ = "news_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<NewsCategory(name='{self.name}', sort_order={self.sort_order})>"


class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True)
    description = Column(String(500))
    content = Column(Text)
    category_id = Column(Integer)
    image = Column(String(500))
    author = Column(String(100))
    publish_time = Column(DateTime)
    views = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<News(title='{self.title}', category_id={self.category_id})>"