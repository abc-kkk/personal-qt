from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from app.database.database import get_db
from app.database import crud
from app.schemas.stock_trade import StockTrade, StockTradeCreate, StockTradeUpdate

router = APIRouter(
    prefix="/stock-trades",
    tags=["stock_trades"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=StockTrade, status_code=status.HTTP_201_CREATED)
def create_stock_trade(stock_trade: StockTradeCreate, db: Session = Depends(get_db)):
    """
    创建新股票交易记录
    
    @param stock_trade: 股票交易创建模式
    @param db: 数据库会话
    @returns: 创建的股票交易记录
    """
    # 检查分类是否存在
    category = crud.get_category(db, category_id=stock_trade.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    db_stock_trade = crud.create_stock_trade(db=db, stock_trade=stock_trade)
    
    # 计算盈亏（如果已卖出）
    profit_data = crud.calculate_profit(db_stock_trade)
    
    # 将计算结果添加到返回对象
    result = StockTrade.model_validate(db_stock_trade)
    result.profit_amount = profit_data["profit_amount"]
    result.profit_percentage = profit_data["profit_percentage"]
    
    return result

@router.get("/", response_model=List[StockTrade])
def read_stock_trades(
    skip: int = 0, 
    limit: int = 100, 
    category_id: Optional[uuid.UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    sort_by: Optional[str] = Query(None, regex="^(buy_date|profit_amount|profit_percentage)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """
    获取股票交易记录列表，支持筛选和排序
    
    @param skip: 跳过的记录数
    @param limit: 返回的最大记录数
    @param category_id: 按分类ID筛选
    @param start_date: 按开始日期筛选
    @param end_date: 按结束日期筛选
    @param sort_by: 排序字段，支持buy_date、profit_amount、profit_percentage
    @param sort_order: 排序顺序，"asc"或"desc"
    @param db: 数据库会话
    @returns: 股票交易记录列表
    """
    stock_trades = crud.get_stock_trades(
        db, 
        skip=skip, 
        limit=limit,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by if sort_by == "buy_date" else None,  # 数据库只能按buy_date排序
        sort_order=sort_order
    )
    
    # 计算每个交易的盈亏
    result = []
    for trade in stock_trades:
        profit_data = crud.calculate_profit(trade)
        trade_with_profit = StockTrade.model_validate(trade)
        trade_with_profit.profit_amount = profit_data["profit_amount"]
        trade_with_profit.profit_percentage = profit_data["profit_percentage"]
        result.append(trade_with_profit)
    
    # 如果需要按盈亏排序，在内存中进行排序
    if sort_by in ["profit_amount", "profit_percentage"]:
        # 过滤掉未卖出的交易（盈亏为None）
        sold_trades = [trade for trade in result if getattr(trade, sort_by) is not None]
        unsold_trades = [trade for trade in result if getattr(trade, sort_by) is None]
        
        # 按指定字段排序
        sold_trades.sort(
            key=lambda x: getattr(x, sort_by),
            reverse=(sort_order == "desc")
        )
        
        # 合并结果，已卖出的在前，未卖出的在后
        result = sold_trades + unsold_trades
    
    return result

@router.get("/{stock_trade_id}", response_model=StockTrade)
def read_stock_trade(stock_trade_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    通过ID获取股票交易记录
    
    @param stock_trade_id: 股票交易ID
    @param db: 数据库会话
    @returns: 股票交易记录
    @raises: 404 如果股票交易记录不存在
    """
    db_stock_trade = crud.get_stock_trade(db, stock_trade_id=stock_trade_id)
    if db_stock_trade is None:
        raise HTTPException(status_code=404, detail="股票交易记录不存在")
    
    # 计算盈亏
    profit_data = crud.calculate_profit(db_stock_trade)
    
    # 将计算结果添加到返回对象
    result = StockTrade.model_validate(db_stock_trade)
    result.profit_amount = profit_data["profit_amount"]
    result.profit_percentage = profit_data["profit_percentage"]
    
    return result

@router.put("/{stock_trade_id}", response_model=StockTrade)
def update_stock_trade(stock_trade_id: uuid.UUID, stock_trade: StockTradeUpdate, db: Session = Depends(get_db)):
    """
    更新股票交易记录
    
    @param stock_trade_id: 股票交易ID
    @param stock_trade: 股票交易更新模式
    @param db: 数据库会话
    @returns: 更新后的股票交易记录
    @raises: 404 如果股票交易记录不存在
    """
    # 检查交易记录是否存在
    db_stock_trade = crud.get_stock_trade(db, stock_trade_id=stock_trade_id)
    if db_stock_trade is None:
        raise HTTPException(status_code=404, detail="股票交易记录不存在")
    
    # 如果更新了分类，检查分类是否存在
    if stock_trade.category_id:
        category = crud.get_category(db, category_id=stock_trade.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="分类不存在")
    
    # 更新交易记录
    db_stock_trade = crud.update_stock_trade(db, stock_trade_id=stock_trade_id, stock_trade=stock_trade)
    
    # 计算盈亏
    profit_data = crud.calculate_profit(db_stock_trade)
    
    # 将计算结果添加到返回对象
    result = StockTrade.model_validate(db_stock_trade)
    result.profit_amount = profit_data["profit_amount"]
    result.profit_percentage = profit_data["profit_percentage"]
    
    return result

@router.delete("/{stock_trade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stock_trade(stock_trade_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    删除股票交易记录
    
    @param stock_trade_id: 股票交易ID
    @param db: 数据库会话
    @raises: 404 如果股票交易记录不存在
    """
    db_stock_trade = crud.get_stock_trade(db, stock_trade_id=stock_trade_id)
    if db_stock_trade is None:
        raise HTTPException(status_code=404, detail="股票交易记录不存在")
    
    crud.delete_stock_trade(db, stock_trade_id=stock_trade_id) 