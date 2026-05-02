from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class NewsCategoryBase(BaseModel):
    name: str
    sort_order: int = 0


class NewsCategoryCreate(NewsCategoryBase):
    pass


class NewsCategory(NewsCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NewsBase(BaseModel):
    title: str
    description: str
    content: str
    category_id: int
    image: Optional[str] = None
    author: Optional[str] = None
    publish_time: Optional[datetime] = None


class NewsCreate(NewsBase):
    pass


class News(NewsBase):
    id: int
    views: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NewsListResponse(BaseModel):
    list: List[News]
    total: int
    hasMore: bool


class NewsDetailResponse(BaseModel):
    id: int
    title: str
    content: str
    image: Optional[str] = None
    author: Optional[str] = None
    publishTime: Optional[str] = None
    categoryId: int
    views: int
    relatedNews: List = []
    
    class Config:
        from_attributes = True