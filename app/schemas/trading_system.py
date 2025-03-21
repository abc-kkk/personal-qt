from pydantic import BaseModel, UUID4, Field
from typing import Optional
from datetime import datetime

class TradingSystemBase(BaseModel):
    """交易系统基础模式"""
    title: str = Field(..., max_length=100, description="标题")
    content: str = Field(..., description="内容")
    is_active: bool = Field(True, description="是否激活")
    sort_order: int = Field(0, description="排序顺序")

class TradingSystemCreate(TradingSystemBase):
    """创建交易系统的数据模式"""
    pass

class TradingSystemUpdate(BaseModel):
    """更新交易系统的数据模式"""
    title: Optional[str] = Field(None, max_length=100, description="标题")
    content: Optional[str] = Field(None, description="内容")
    is_active: Optional[bool] = Field(None, description="是否激活")
    sort_order: Optional[int] = Field(None, description="排序顺序")

class TradingSystem(TradingSystemBase):
    """交易系统响应模式"""
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 