from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date, timedelta
from uuid import UUID

from app.database.database import get_db
from app.models.models import DailyFund
from app.schemas.daily_fund import DailyFund as DailyFundSchema
from app.schemas.daily_fund import DailyFundCreate, DailyFundUpdate

router = APIRouter(
    prefix="/daily-funds",
    tags=["每日资金"],
    responses={404: {"description": "未找到"}},
)

@router.post("/", response_model=DailyFundSchema)
def create_daily_fund(daily_fund: DailyFundCreate, db: Session = Depends(get_db)):
    """
    创建新的每日资金记录
    
    @param daily_fund: 每日资金数据
    @param db: 数据库会话
    @returns: 创建的每日资金记录
    """
    # 检查日期是否已存在
    db_daily_fund = db.query(DailyFund).filter(DailyFund.fund_date == daily_fund.fund_date).first()
    if db_daily_fund:
        raise HTTPException(status_code=400, detail=f"日期 {daily_fund.fund_date} 的资金记录已存在")
    
    # 创建新记录
    db_daily_fund = DailyFund(**daily_fund.dict())
    db.add(db_daily_fund)
    db.commit()
    db.refresh(db_daily_fund)
    return db_daily_fund

@router.get("/", response_model=List[DailyFundSchema])
def read_daily_funds(
    skip: int = 0, 
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    获取每日资金记录列表
    
    @param skip: 跳过的记录数
    @param limit: 返回的最大记录数
    @param start_date: 开始日期
    @param end_date: 结束日期
    @param db: 数据库会话
    @returns: 每日资金记录列表
    """
    query = db.query(DailyFund)
    
    if start_date:
        query = query.filter(DailyFund.fund_date >= start_date)
    if end_date:
        query = query.filter(DailyFund.fund_date <= end_date)
    
    return query.order_by(desc(DailyFund.fund_date)).offset(skip).limit(limit).all()

@router.get("/recent", response_model=List[DailyFundSchema])
def read_recent_daily_funds(days: int = Query(30, gt=0, lt=366), db: Session = Depends(get_db)):
    """
    获取最近N天的每日资金记录
    
    @param days: 天数
    @param db: 数据库会话
    @returns: 最近N天的每日资金记录
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    return db.query(DailyFund).filter(
        DailyFund.fund_date >= start_date,
        DailyFund.fund_date <= end_date
    ).order_by(DailyFund.fund_date).all()

@router.get("/{daily_fund_id}", response_model=DailyFundSchema)
def read_daily_fund(daily_fund_id: UUID, db: Session = Depends(get_db)):
    """
    获取指定ID的每日资金记录
    
    @param daily_fund_id: 每日资金记录ID
    @param db: 数据库会话
    @returns: 每日资金记录
    """
    db_daily_fund = db.query(DailyFund).filter(DailyFund.id == daily_fund_id).first()
    if db_daily_fund is None:
        raise HTTPException(status_code=404, detail="每日资金记录未找到")
    return db_daily_fund

@router.get("/date/{fund_date}", response_model=DailyFundSchema)
def read_daily_fund_by_date(fund_date: date, db: Session = Depends(get_db)):
    """
    获取指定日期的每日资金记录
    
    @param fund_date: 资金日期
    @param db: 数据库会话
    @returns: 每日资金记录
    """
    db_daily_fund = db.query(DailyFund).filter(DailyFund.fund_date == fund_date).first()
    if db_daily_fund is None:
        raise HTTPException(status_code=404, detail=f"日期 {fund_date} 的资金记录未找到")
    return db_daily_fund

@router.put("/{daily_fund_id}", response_model=DailyFundSchema)
def update_daily_fund(daily_fund_id: UUID, daily_fund: DailyFundUpdate, db: Session = Depends(get_db)):
    """
    更新每日资金记录
    
    @param daily_fund_id: 每日资金记录ID
    @param daily_fund: 更新的每日资金数据
    @param db: 数据库会话
    @returns: 更新后的每日资金记录
    """
    db_daily_fund = db.query(DailyFund).filter(DailyFund.id == daily_fund_id).first()
    if db_daily_fund is None:
        raise HTTPException(status_code=404, detail="每日资金记录未找到")
    
    # 更新非空字段
    update_data = daily_fund.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_daily_fund, key, value)
    
    db.commit()
    db.refresh(db_daily_fund)
    return db_daily_fund

@router.delete("/{daily_fund_id}", response_model=dict)
def delete_daily_fund(daily_fund_id: UUID, db: Session = Depends(get_db)):
    """
    删除每日资金记录
    
    @param daily_fund_id: 每日资金记录ID
    @param db: 数据库会话
    @returns: 操作结果
    """
    db_daily_fund = db.query(DailyFund).filter(DailyFund.id == daily_fund_id).first()
    if db_daily_fund is None:
        raise HTTPException(status_code=404, detail="每日资金记录未找到")
    
    db.delete(db_daily_fund)
    db.commit()
    return {"detail": "每日资金记录已删除"} 