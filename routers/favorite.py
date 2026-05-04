from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.favorite import (
    add_favorite,
    check_favorite_status,
    clear_favorites,
    get_favorite_count,
    get_favorite_list,
    news_exists,
    remove_favorite,
)
from models.users import User
from schemas.favorite import (
    FavoriteAddRequest,
    FavoriteListResponse,
    FavoriteNewsItemResponse,
    FavoriteResponse,
)
from utils.auth import get_current_user
from utils.response import success

router = APIRouter(prefix="/api/favorite", tags=["favorite"])


@router.get("/check")
async def check_favorite(
    news_id: int = Query(..., alias="newsId"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """检查当前登录用户是否收藏了指定新闻。"""

    is_favorite = await check_favorite_status(db, current_user.id, news_id)
    return success(data={"isFavorite": is_favorite})


@router.post("/add")
async def add_user_favorite(
    favorite_data: Optional[FavoriteAddRequest] = Body(None),
    news_id: Optional[int] = Query(None, alias="newsId"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """添加收藏。"""

    target_news_id = favorite_data.news_id if favorite_data else news_id
    if target_news_id is None:
        raise HTTPException(status_code=422, detail="newsId不能为空")

    if not await news_exists(db, target_news_id):
        raise HTTPException(status_code=404, detail="新闻不存在")

    favorite = await add_favorite(db, current_user.id, target_news_id)
    return success(
        message="收藏成功",
        data=FavoriteResponse.model_validate(favorite),
    )


@router.delete("/remove")
async def remove_user_favorite(
    news_id: int = Query(..., alias="newsId"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """取消收藏。"""

    removed = await remove_favorite(db, current_user.id, news_id)
    if not removed:
        raise HTTPException(status_code=404, detail="收藏记录不存在")

    return success(message="取消收藏成功", data=None)


@router.get("/list")
async def list_user_favorites(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize", description="每页条数"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户收藏列表。"""

    skip = (page - 1) * page_size
    favorite_rows = await get_favorite_list(db, current_user.id, skip, page_size)
    total_count = await get_favorite_count(db, current_user.id)
    has_more = (skip + len(favorite_rows)) < total_count

    response_list = [
        FavoriteNewsItemResponse(
            id=news.id,
            title=news.title,
            description=news.description,
            image=news.image,
            author=news.author,
            publish_time=news.publish_time,
            category_id=news.category_id,
            views=news.views,
            favorite_time=favorite_time,
        )
        for news, favorite_time in favorite_rows
    ]

    return success(
        data=FavoriteListResponse(
            list=response_list,
            total=total_count,
            has_more=has_more,
        )
    )


@router.delete("/clear")
async def clear_user_favorites(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """清空当前用户全部收藏。"""

    deleted_count = await clear_favorites(db, current_user.id)
    return success(message=f"成功删除{deleted_count}条收藏记录", data=None)
