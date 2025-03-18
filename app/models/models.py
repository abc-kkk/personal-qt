from sqlalchemy import Column, String, Integer, Float, DateTime, Date, ForeignKey, Text, ARRAY, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database.database import Base

class Category(Base):
    """
    分类表模型
    """
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    trades = relationship("StockTrade", back_populates="category")

class StockTrade(Base):
    """
    交易记录表模型
    """
    __tablename__ = "stock_trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stock_code = Column(String(10), nullable=False)
    stock_name = Column(String(50), nullable=False)
    buy_date = Column(DateTime, nullable=False)
    buy_price = Column(Numeric(10, 2), nullable=False)
    buy_quantity = Column(Integer, nullable=False)
    sell_date = Column(DateTime, nullable=True)
    sell_price = Column(Numeric(10, 2), nullable=True)
    screenshot_url = Column(ARRAY(Text), nullable=True)
    buy_reason = Column(Text, nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    category = relationship("Category", back_populates="trades")

class FailureCase(Base):
    """
    失败案例表模型
    """
    __tablename__ = "failure_cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stock_code = Column(String(10), nullable=False)
    stock_name = Column(String(50), nullable=False)
    images = Column(ARRAY(Text), nullable=False)
    reason = Column(Text, nullable=False)
    lessons = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DailyReview(Base):
    """
    每日复盘表模型
    """
    __tablename__ = "daily_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_date = Column(Date, nullable=False)
    market_index = Column(Numeric(10, 2), nullable=False)
    trading_amount = Column(Numeric(10, 2), nullable=False)
    market_change_rate = Column(Numeric(5, 2), nullable=False)
    limit_up_count = Column(Integer, nullable=False)
    limit_down_count = Column(Integer, nullable=False)
    rise_count = Column(Integer, nullable=False)
    fall_count = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 