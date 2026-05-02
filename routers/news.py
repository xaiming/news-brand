from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud.news import get_news_categories, get_news_list, get_news_detail, increment_news_views
from typing import List, Optional
from models.news import NewsCategory, News

# 创建路由
router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/categories")
async def get_categories(
    skip: int = Query(0, description="跳过的记录数"), 
    limit: int = Query(100, description="返回的记录数限制"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取新闻分类列表
    """
    categories = await get_news_categories(db, skip, limit)
    return {
        "code": 200,
        "message": "success",
        "data": categories
    }


@router.get("/list")
async def get_news_list_api(
    category_id: int = Query(..., description="分类ID"),
    page: int = Query(1, description="页码"),
    pageSize: int = Query(10, description="每页显示的新闻数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取新闻列表
    """
    result = await get_news_list(db, category_id, page, pageSize)
    return {
        "code": 200,
        "message": "success",
        "data": result
    }


@router.get("/detail")
async def get_news_detail_api(
    id: int = Query(..., description="新闻ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取新闻详情
    """
    news = await get_news_detail(db, id)
    if not news:
        return {
            "code": 404,
            "message": "新闻不存在",
            "data": None
        }
    
    # 增加浏览量
    await increment_news_views(db, id)
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": news.id,
            "title": news.title,
            "content": news.content,
            "image": news.image,
            "author": news.author,
            "publishTime": news.publish_time.isoformat() if news.publish_time else None,
            "categoryId": news.category_id,
            "views": news.views,
            "relatedNews": []
        }
    }