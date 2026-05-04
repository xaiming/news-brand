from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News


async def check_favorite_status(db: AsyncSession, user_id: int, news_id: int) -> bool:
    """检查指定用户是否收藏了指定新闻。"""

    query = await db.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.news_id == news_id,
        )
    )
    return query.scalar_one_or_none() is not None


async def get_favorite_by_user_and_news(
    db: AsyncSession,
    user_id: int,
    news_id: int,
):
    """查询某个用户对某条新闻的收藏记录。"""

    query = await db.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.news_id == news_id,
        )
    )
    return query.scalar_one_or_none()


async def news_exists(db: AsyncSession, news_id: int) -> bool:
    """检查新闻是否存在，避免收藏不存在的新闻。"""

    query = await db.execute(select(News.id).where(News.id == news_id))
    return query.scalar_one_or_none() is not None


async def add_favorite(db: AsyncSession, user_id: int, news_id: int):
    """添加收藏；如果已经收藏过，直接返回已有收藏记录。"""

    favorite = await get_favorite_by_user_and_news(db, user_id, news_id)
    if favorite:
        return favorite

    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite


async def remove_favorite(db: AsyncSession, user_id: int, news_id: int) -> bool:
    """取消收藏，返回是否真的删除了记录。"""

    query = delete(Favorite).where(
        Favorite.user_id == user_id,
        Favorite.news_id == news_id,
    )
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0


async def get_favorite_list(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 10,
):
    """分页获取当前用户收藏的新闻列表。"""

    query = (
        select(News, Favorite.created_at)
        .join(Favorite, Favorite.news_id == News.id)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.all()


async def get_favorite_count(db: AsyncSession, user_id: int) -> int:
    """获取当前用户收藏总数。"""

    query = await db.execute(
        select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
    )
    return query.scalar_one()


async def clear_favorites(db: AsyncSession, user_id: int) -> int:
    """清空当前用户全部收藏，返回删除条数。"""

    query = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount
