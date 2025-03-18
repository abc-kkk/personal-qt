from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal

class DailyFundBase(BaseModel):
    """每日资金基础模型"""
    fund_date: date = Field(..., description="资金日期")
    total_amount: Decimal = Field(..., description="总资金")
    notes: Optional[str] = Field(None, description="备注")

    @validator('total_amount')
    def validate_total_amount(cls, v):
        """验证总资金不能为负"""
        if v < 0:
            raise ValueError('总资金不能为负')
        return v

class DailyFundCreate(DailyFundBase):
    """用于创建每日资金的模型"""
    pass

class DailyFundUpdate(BaseModel):
    """用于更新每日资金的模型"""
    fund_date: Optional[date] = None
    total_amount: Optional[Decimal] = None
    notes: Optional[str] = None

class DailyFund(DailyFundBase):
    """完整的每日资金模型，包含ID和创建/更新时间"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 