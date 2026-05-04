from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import news
from schemas.news import CategoryResponse, NewsDetailResponse, NewsListResponse
from utils.response import success

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/categories")
async def get_categories(
    skip: int = Query(0, description="跳过的记录数"),
    limit: int = Query(100, description="返回的记录数限制"),
    db: AsyncSession = Depends(get_db),
):
    categories = await news.get_categories(db, skip, limit)
    # 将 ORM 对象列表转换为响应模型，统一处理字段别名和序列化。
    response_data = [CategoryResponse.model_validate(category) for category in categories]
    return success(data=response_data)


@router.get("/list")
async def get_news_list(
    category_id: int = Query(..., alias="categoryId", description="新闻分类ID"),
    page: int = Query(1, description="当前页码"),
    page_size: int = Query(10, le=100, alias="pageSize", description="每页记录数"),
    db: AsyncSession = Depends(get_db),
):
    # 前端传页码，数据库查询使用 offset。
    skip = (page - 1) * page_size

    news_list = await news.get_news_list(db, category_id, skip, page_size)
    total_count = await news.get_news_count(db, category_id)
    has_more = (skip + len(news_list)) < total_count

    # 分页信息和新闻列表一起交给 schema 输出前端字段格式。
    response_data = NewsListResponse(
        list=news_list,
        total=total_count,
        has_more=has_more,
    )
    return success(data=response_data)


@router.get("/detail")
async def get_news_detail(
    news_id: int = Query(..., description="新闻ID"),
    db: AsyncSession = Depends(get_db),
):
    news_detail = await news.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")

    # 详情页访问成功后递增浏览量；更新失败时按新闻不存在处理。
    views_res = await news.increment_views(db, news_detail.id)
    if not views_res:
        raise HTTPException(status_code=404, detail="新闻不存在")

    related_news = await news.get_related_news(
        db,
        news_detail.category_id,
        news_detail.id,
    )

    # 详情字段来自当前新闻，相关新闻复用 NewsItemResponse 序列化。
    response_data = NewsDetailResponse(
        id=news_detail.id,
        title=news_detail.title,
        content=news_detail.content,
        image=news_detail.image,
        author=news_detail.author,
        publish_time=news_detail.publish_time,
        category_id=news_detail.category_id,
        views=news_detail.views,
        related_news=related_news,
    )
    return success(data=response_data)
