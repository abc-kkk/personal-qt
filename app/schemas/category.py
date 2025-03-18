from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime
import uuid

class CategoryBase(BaseModel):
    """
    分类基础模式
    """
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    """
    创建分类的请求模式
    """
    pass

class CategoryUpdate(CategoryBase):
    """
    更新分类的请求模式
    """
    pass

class CategoryInDB(CategoryBase):
    """
    数据库中的分类模式
    """
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class Category(CategoryInDB):
    """
    返回给客户端的分类模式
    """
    pass 