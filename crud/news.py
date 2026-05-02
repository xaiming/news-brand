import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from models.news import News, NewsCategory
from typing import List, Optional


async def get_news_categories(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[NewsCategory]:
    """
    获取新闻分类列表
    """
    stmt = select(NewsCategory).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_news_list(db: AsyncSession, category_id: int, page: int = 1, page_size: int = 10) -> dict:
    """
    获取新闻列表
    """
    skip = (page - 1) * page_size
    
    # 获取新闻列表
    stmt = select(News).where(News.category_id == category_id, News.is_active == True).offset(skip).limit(page_size)
    result = await db.execute(stmt)
    news_list = result.scalars().all()
    
    # 获取总数
    count_stmt = select(News).where(News.category_id == category_id, News.is_active == True)
    count_result = await db.execute(count_stmt)
    total = len(count_result.scalars().all())
    
    return {
        "list": news_list,
        "total": total,
        "hasMore": len(news_list) == page_size
    }


async def get_news_detail(db: AsyncSession, news_id: int) -> Optional[News]:
    """
    获取新闻详情
    """
    stmt = select(News).where(News.id == news_id, News.is_active == True)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def increment_news_views(db: AsyncSession, news_id: int):
    """
    增加新闻浏览量
    """
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    await db.execute(stmt)
    await db.commit()


async def create_news_category(db: AsyncSession, name: str, sort_order: int = 0) -> NewsCategory:
    """
    创建新闻分类
    """
    category = NewsCategory(name=name, sort_order=sort_order)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def create_news(db: AsyncSession, title: str, description: str, content: str, 
                      category_id: int, image: str = None, author: str = None, 
                      publish_time: datetime.datetime = None) -> News:
    """
    创建新闻
    """
    if publish_time is None:
        publish_time = datetime.datetime.utcnow()
        
    news = News(
        title=title,
        description=description,
        content=content,
        category_id=category_id,
        image=image,
        author=author,
        publish_time=publish_time
    )
    db.add(news)
    await db.commit()
    await db.refresh(news)
    return news