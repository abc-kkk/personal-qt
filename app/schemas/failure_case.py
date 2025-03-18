from pydantic import BaseModel, UUID4
from typing import List, Optional
from datetime import datetime
import uuid

class FailureCaseBase(BaseModel):
    """
    失败案例基础模式
    """
    stock_code: str
    stock_name: str
    images: List[str]
    reason: str
    lessons: str

class FailureCaseCreate(FailureCaseBase):
    """
    创建失败案例的请求模式
    """
    pass

class FailureCaseUpdate(BaseModel):
    """
    更新失败案例的请求模式
    """
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None
    images: Optional[List[str]] = None
    reason: Optional[str] = None
    lessons: Optional[str] = None

class FailureCaseInDB(FailureCaseBase):
    """
    数据库中的失败案例模式
    """
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class FailureCase(FailureCaseInDB):
    """
    返回给客户端的失败案例模式
    """
    pass 