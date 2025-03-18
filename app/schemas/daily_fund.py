from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal

class DailyFundBase(BaseModel):
    """每日资金基础模型"""
    fund_date: date = Field(..., description="资金日期")
    total_amount: Decimal = Field(..., description="总资金")
    stock_amount: Decimal = Field(..., description="股票市值")
    cash_amount: Decimal = Field(..., description="现金")
    profit_amount: Optional[Decimal] = Field(None, description="当日盈亏")
    profit_rate: Optional[Decimal] = Field(None, description="当日收益率(%)")
    cumulative_profit_rate: Optional[Decimal] = Field(None, description="累计收益率(%)")
    notes: Optional[str] = Field(None, description="备注")

    @validator('cash_amount')
    def validate_cash_amount(cls, v, values):
        """验证现金不能大于总资金"""
        if 'total_amount' in values and v > values['total_amount']:
            raise ValueError('现金金额不能大于总资金')
        return v

    @validator('stock_amount')
    def validate_stock_amount(cls, v, values):
        """验证股票市值不能大于总资金"""
        if 'total_amount' in values and v > values['total_amount']:
            raise ValueError('股票市值不能大于总资金')
        return v

class DailyFundCreate(DailyFundBase):
    """用于创建每日资金的模型"""
    pass

class DailyFundUpdate(BaseModel):
    """用于更新每日资金的模型"""
    fund_date: Optional[date] = None
    total_amount: Optional[Decimal] = None
    stock_amount: Optional[Decimal] = None
    cash_amount: Optional[Decimal] = None
    profit_amount: Optional[Decimal] = None
    profit_rate: Optional[Decimal] = None
    cumulative_profit_rate: Optional[Decimal] = None
    notes: Optional[str] = None

class DailyFund(DailyFundBase):
    """完整的每日资金模型，包含ID和创建/更新时间"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 