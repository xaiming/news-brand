from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryResponse(BaseModel):
    """新闻分类响应模型，对应 /api/news/categories。"""

    id: int
    name: str
    sort_order: int = Field(..., alias="sortOrder")

    # from_attributes 支持直接从 SQLAlchemy ORM 对象读取字段。
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class NewsItemResponse(BaseModel):
    """新闻列表项响应模型，供列表、详情和相关新闻复用。"""

    id: int
    title: str
    content: str
    image: Optional[str] = None
    author: Optional[str] = None
    # alias 将后端蛇形字段转换为前端需要的驼峰字段。
    publish_time: datetime = Field(..., alias="publishTime")
    category_id: int = Field(..., alias="categoryId")
    views: int

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class NewsListResponse(BaseModel):
    """新闻分页列表响应模型，对应 /api/news/list 的 data。"""

    list: List[NewsItemResponse]
    total: int
    has_more: bool = Field(..., alias="hasMore")

    model_config = ConfigDict(populate_by_name=True)


class NewsDetailResponse(NewsItemResponse):
    """新闻详情响应模型，在新闻基础信息上追加相关新闻。"""

    related_news: List[NewsItemResponse] = Field(default_factory=list, alias="relatedNews")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
