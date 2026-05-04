from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class FavoriteAddRequest(BaseModel):
    """添加收藏请求体。"""

    news_id: int = Field(..., alias="newsId", description="新闻ID")

    model_config = ConfigDict(populate_by_name=True)


class FavoriteResponse(BaseModel):
    """添加收藏成功后的收藏记录响应。"""

    id: int
    user_id: int = Field(..., alias="userId")
    news_id: int = Field(..., alias="newsId")
    created_at: datetime = Field(..., alias="createTime")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class FavoriteNewsItemResponse(BaseModel):
    """收藏列表里的新闻信息。"""

    id: int
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    publish_time: datetime = Field(..., alias="publishTime")
    category_id: int = Field(..., alias="categoryId")
    views: int
    favorite_time: datetime = Field(..., alias="favoriteTime")

    model_config = ConfigDict(populate_by_name=True)


class FavoriteListResponse(BaseModel):
    """收藏分页列表响应。"""

    list: List[FavoriteNewsItemResponse]
    total: int
    has_more: bool = Field(..., alias="hasMore")

    model_config = ConfigDict(populate_by_name=True)
