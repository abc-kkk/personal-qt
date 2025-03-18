from pydantic import BaseModel, UUID4, condecimal
from typing import Optional
from datetime import datetime, date
import uuid

class DailyReviewBase(BaseModel):
    """
    每日复盘基础模式
    """
    review_date: date
    market_index: condecimal(max_digits=10, decimal_places=2)
    trading_amount: condecimal(max_digits=10, decimal_places=2)
    market_change_rate: condecimal(max_digits=5, decimal_places=2)
    limit_up_count: int
    limit_down_count: int
    rise_count: int
    fall_count: int
    content: str

class DailyReviewCreate(DailyReviewBase):
    """
    创建每日复盘的请求模式
    """
    pass

class DailyReviewUpdate(BaseModel):
    """
    更新每日复盘的请求模式
    """
    review_date: Optional[date] = None
    market_index: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    trading_amount: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    market_change_rate: Optional[condecimal(max_digits=5, decimal_places=2)] = None
    limit_up_count: Optional[int] = None
    limit_down_count: Optional[int] = None
    rise_count: Optional[int] = None
    fall_count: Optional[int] = None
    content: Optional[str] = None

class DailyReviewInDB(DailyReviewBase):
    """
    数据库中的每日复盘模式
    """
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class DailyReview(DailyReviewInDB):
    """
    返回给客户端的每日复盘模式
    """
    pass 