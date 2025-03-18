from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, and_, or_
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
import uuid
from decimal import Decimal

from app.models.models import Category, StockTrade, FailureCase, DailyReview
from app.schemas import category as category_schema
from app.schemas import stock_trade as stock_trade_schema
from app.schemas import failure_case as failure_case_schema
from app.schemas import daily_review as daily_review_schema

# 分类CRUD操作
def create_category(db: Session, category: category_schema.CategoryCreate) -> Category:
    """
    创建新分类
    
    @param db: 数据库会话
    @param category: 分类创建模式
    @returns: 创建的分类对象
    """
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_category(db: Session, category_id: uuid.UUID) -> Optional[Category]:
    """
    通过ID获取分类
    
    @param db: 数据库会话
    @param category_id: 分类ID
    @returns: 分类对象，如果不存在则返回None
    """
    return db.query(Category).filter(Category.id == category_id).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    """
    获取分类列表
    
    @param db: 数据库会话
    @param skip: 跳过的记录数
    @param limit: 返回的最大记录数
    @returns: 分类对象列表
    """
    return db.query(Category).offset(skip).limit(limit).all()

def update_category(db: Session, category_id: uuid.UUID, category: category_schema.CategoryUpdate) -> Optional[Category]:
    """
    更新分类
    
    @param db: 数据库会话
    @param category_id: 分类ID
    @param category: 分类更新模式
    @returns: 更新后的分类对象，如果不存在则返回None
    """
    db_category = get_category(db, category_id)
    if db_category:
        update_data = category.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_category, key, value)
        db_category.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: uuid.UUID) -> bool:
    """
    删除分类
    
    @param db: 数据库会话
    @param category_id: 分类ID
    @returns: 是否成功删除
    """
    db_category = get_category(db, category_id)
    if db_category:
        # 检查是否有关联的交易记录
        trades = db.query(StockTrade).filter(StockTrade.category_id == category_id).first()
        if trades:
            return False
        db.delete(db_category)
        db.commit()
        return True
    return False

# 股票交易CRUD操作
def create_stock_trade(db: Session, stock_trade: stock_trade_schema.StockTradeCreate) -> StockTrade:
    """
    创建新股票交易记录
    
    @param db: 数据库会话
    @param stock_trade: 股票交易创建模式
    @returns: 创建的股票交易对象
    """
    db_stock_trade = StockTrade(**stock_trade.dict())
    db.add(db_stock_trade)
    db.commit()
    db.refresh(db_stock_trade)
    return db_stock_trade

def get_stock_trade(db: Session, stock_trade_id: uuid.UUID) -> Optional[StockTrade]:
    """
    通过ID获取股票交易记录
    
    @param db: 数据库会话
    @param stock_trade_id: 股票交易ID
    @returns: 股票交易对象，如果不存在则返回None
    """
    return db.query(StockTrade).filter(StockTrade.id == stock_trade_id).first()

def get_stock_trades(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    category_id: Optional[uuid.UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "desc"
) -> List[StockTrade]:
    """
    获取股票交易记录列表，支持筛选和排序
    
    @param db: 数据库会话
    @param skip: 跳过的记录数
    @param limit: 返回的最大记录数
    @param category_id: 按分类ID筛选
    @param start_date: 按开始日期筛选
    @param end_date: 按结束日期筛选
    @param sort_by: 排序字段
    @param sort_order: 排序顺序，"asc"或"desc"
    @returns: 股票交易对象列表
    """
    query = db.query(StockTrade)
    
    # 应用筛选条件
    if category_id:
        query = query.filter(StockTrade.category_id == category_id)
    if start_date:
        query = query.filter(StockTrade.buy_date >= start_date)
    if end_date:
        query = query.filter(StockTrade.buy_date <= end_date)
    
    # 应用排序
    if sort_by:
        if sort_by == "buy_date":
            if sort_order == "asc":
                query = query.order_by(asc(StockTrade.buy_date))
            else:
                query = query.order_by(desc(StockTrade.buy_date))
    else:
        # 默认按买入日期倒序排序
        query = query.order_by(desc(StockTrade.buy_date))
    
    return query.offset(skip).limit(limit).all()

def update_stock_trade(db: Session, stock_trade_id: uuid.UUID, stock_trade: stock_trade_schema.StockTradeUpdate) -> Optional[StockTrade]:
    """
    更新股票交易记录
    
    @param db: 数据库会话
    @param stock_trade_id: 股票交易ID
    @param stock_trade: 股票交易更新模式
    @returns: 更新后的股票交易对象，如果不存在则返回None
    """
    db_stock_trade = get_stock_trade(db, stock_trade_id)
    if db_stock_trade:
        update_data = stock_trade.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_stock_trade, key, value)
        db_stock_trade.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_stock_trade)
    return db_stock_trade

def delete_stock_trade(db: Session, stock_trade_id: uuid.UUID) -> bool:
    """
    删除股票交易记录
    
    @param db: 数据库会话
    @param stock_trade_id: 股票交易ID
    @returns: 是否成功删除
    """
    db_stock_trade = get_stock_trade(db, stock_trade_id)
    if db_stock_trade:
        db.delete(db_stock_trade)
        db.commit()
        return True
    return False

def calculate_profit(stock_trade: StockTrade) -> Dict[str, Optional[Decimal]]:
    """
    计算股票交易的盈亏
    
    @param stock_trade: 股票交易对象
    @returns: 包含盈亏金额和盈亏幅度的字典
    """
    result = {"profit_amount": None, "profit_percentage": None}
    
    if stock_trade.sell_date and stock_trade.sell_price:
        # 计算盈亏金额
        buy_total = stock_trade.buy_price * stock_trade.buy_quantity
        sell_total = stock_trade.sell_price * stock_trade.buy_quantity
        profit_amount = sell_total - buy_total
        
        # 计算盈亏幅度
        profit_percentage = (profit_amount / buy_total) * 100
        
        result["profit_amount"] = profit_amount
        result["profit_percentage"] = profit_percentage
    
    return result

# 失败案例CRUD操作
def create_failure_case(db: Session, failure_case: failure_case_schema.FailureCaseCreate) -> FailureCase:
    """
    创建新失败案例
    
    @param db: 数据库会话
    @param failure_case: 失败案例创建模式
    @returns: 创建的失败案例对象
    """
    db_failure_case = FailureCase(**failure_case.dict())
    db.add(db_failure_case)
    db.commit()
    db.refresh(db_failure_case)
    return db_failure_case

def get_failure_case(db: Session, failure_case_id: uuid.UUID) -> Optional[FailureCase]:
    """
    通过ID获取失败案例
    
    @param db: 数据库会话
    @param failure_case_id: 失败案例ID
    @returns: 失败案例对象，如果不存在则返回None
    """
    return db.query(FailureCase).filter(FailureCase.id == failure_case_id).first()

def get_failure_cases(db: Session, skip: int = 0, limit: int = 100) -> List[FailureCase]:
    """
    获取失败案例列表
    
    @param db: 数据库会话
    @param skip: 跳过的记录数
    @param limit: 返回的最大记录数
    @returns: 失败案例对象列表
    """
    return db.query(FailureCase).order_by(desc(FailureCase.created_at)).offset(skip).limit(limit).all()

def update_failure_case(db: Session, failure_case_id: uuid.UUID, failure_case: failure_case_schema.FailureCaseUpdate) -> Optional[FailureCase]:
    """
    更新失败案例
    
    @param db: 数据库会话
    @param failure_case_id: 失败案例ID
    @param failure_case: 失败案例更新模式
    @returns: 更新后的失败案例对象，如果不存在则返回None
    """
    db_failure_case = get_failure_case(db, failure_case_id)
    if db_failure_case:
        update_data = failure_case.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_failure_case, key, value)
        db_failure_case.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_failure_case)
    return db_failure_case

def delete_failure_case(db: Session, failure_case_id: uuid.UUID) -> bool:
    """
    删除失败案例
    
    @param db: 数据库会话
    @param failure_case_id: 失败案例ID
    @returns: 是否成功删除
    """
    db_failure_case = get_failure_case(db, failure_case_id)
    if db_failure_case:
        db.delete(db_failure_case)
        db.commit()
        return True
    return False

# 每日复盘CRUD操作
def create_daily_review(db: Session, daily_review: daily_review_schema.DailyReviewCreate) -> DailyReview:
    """
    创建新每日复盘
    
    @param db: 数据库会话
    @param daily_review: 每日复盘创建模式
    @returns: 创建的每日复盘对象
    """
    db_daily_review = DailyReview(**daily_review.dict())
    db.add(db_daily_review)
    db.commit()
    db.refresh(db_daily_review)
    return db_daily_review

def get_daily_review(db: Session, daily_review_id: uuid.UUID) -> Optional[DailyReview]:
    """
    通过ID获取每日复盘
    
    @param db: 数据库会话
    @param daily_review_id: 每日复盘ID
    @returns: 每日复盘对象，如果不存在则返回None
    """
    return db.query(DailyReview).filter(DailyReview.id == daily_review_id).first()

def get_daily_review_by_date(db: Session, review_date: date) -> Optional[DailyReview]:
    """
    通过日期获取每日复盘
    
    @param db: 数据库会话
    @param review_date: 复盘日期
    @returns: 每日复盘对象，如果不存在则返回None
    """
    return db.query(DailyReview).filter(DailyReview.review_date == review_date).first()

def get_daily_reviews(db: Session, skip: int = 0, limit: int = 100) -> List[DailyReview]:
    """
    获取每日复盘列表
    
    @param db: 数据库会话
    @param skip: 跳过的记录数
    @param limit: 返回的最大记录数
    @returns: 每日复盘对象列表
    """
    return db.query(DailyReview).order_by(desc(DailyReview.review_date)).offset(skip).limit(limit).all()

def update_daily_review(db: Session, daily_review_id: uuid.UUID, daily_review: daily_review_schema.DailyReviewUpdate) -> Optional[DailyReview]:
    """
    更新每日复盘
    
    @param db: 数据库会话
    @param daily_review_id: 每日复盘ID
    @param daily_review: 每日复盘更新模式
    @returns: 更新后的每日复盘对象，如果不存在则返回None
    """
    db_daily_review = get_daily_review(db, daily_review_id)
    if db_daily_review:
        update_data = daily_review.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_daily_review, key, value)
        db_daily_review.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_daily_review)
    return db_daily_review

def delete_daily_review(db: Session, daily_review_id: uuid.UUID) -> bool:
    """
    删除每日复盘
    
    @param db: 数据库会话
    @param daily_review_id: 每日复盘ID
    @returns: 是否成功删除
    """
    db_daily_review = get_daily_review(db, daily_review_id)
    if db_daily_review:
        db.delete(db_daily_review)
        db.commit()
        return True
    return False 