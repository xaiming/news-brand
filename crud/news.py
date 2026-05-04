from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category, News


# 新闻 分类
async def get_categories(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


# 获取新闻列表
async def get_news_list(
    db: AsyncSession, category_id: int, skip: int = 0, limit: int = 10
):
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


# 新闻列表数量
async def get_news_count(db: AsyncSession, category_id: int):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()


# 新闻详情
async def get_news_detail(db: AsyncSession, news_id: int):
    stmt = select(News).where(News.id == news_id)

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# 新闻浏览量
async def increment_views(db: AsyncSession, news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()

    return result.rowcount > 0


# 同类相关新闻
async def get_related_news(
    db: AsyncSession, category_id: int, news_id: int, limit: int = 5
):
    stmt = (
        select(News)
        .where(News.category_id == category_id, News.id != news_id)
        .order_by(News.views.desc(), News.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
