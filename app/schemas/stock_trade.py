from pydantic import BaseModel, UUID4, condecimal, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import uuid

class StockTradeBase(BaseModel):
    """
    股票交易基础模式
    """
    stock_code: str
    stock_name: str
    buy_date: datetime
    buy_price: condecimal(max_digits=10, decimal_places=2)
    buy_quantity: int
    buy_reason: str
    category_id: uuid.UUID
    sell_date: Optional[datetime] = None
    sell_price: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    screenshot_url: Optional[List[str]] = None

class StockTradeCreate(StockTradeBase):
    """
    创建股票交易的请求模式
    """
    pass

class StockTradeUpdate(BaseModel):
    """
    更新股票交易的请求模式
    """
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None
    buy_date: Optional[datetime] = None
    buy_price: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    buy_quantity: Optional[int] = None
    buy_reason: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    sell_date: Optional[datetime] = None
    sell_price: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    screenshot_url: Optional[List[str]] = None

class StockTradeInDB(StockTradeBase):
    """
    数据库中的股票交易模式
    """
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class StockTrade(StockTradeInDB):
    """
    返回给客户端的股票交易模式
    """
    # 计算字段
    profit_amount: Optional[Decimal] = None
    profit_percentage: Optional[Decimal] = None

    model_config = {
        "from_attributes": True
    } 