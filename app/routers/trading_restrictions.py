from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.database.database import get_db
from app.database import crud
from app.schemas.trading_restriction import TradingRestriction, TradingRestrictionCreate, TradingRestrictionUpdate

router = APIRouter(
    prefix="/trading-restrictions",
    tags=["交易禁令"],
    responses={404: {"description": "资源未找到"}},
)

@router.post("/", response_model=TradingRestriction)
def create_trading_restriction(
    trading_restriction: TradingRestrictionCreate,
    db: Session = Depends(get_db)
):
    """
    创建交易禁令
    
    @param trading_restriction: 交易禁令创建模式
    @param db: 数据库会话
    @returns: 创建的交易禁令对象
    """
    return crud.create_trading_restriction(db=db, trading_restriction=trading_restriction)

@router.get("/", response_model=List[TradingRestriction])
def read_trading_restrictions(
    skip: int = Query(0, description="跳过的记录数"),
    limit: int = Query(100, description="返回的记录数"),
    only_active: bool = Query(False, description="是否只返回激活的禁令"),
    db: Session = Depends(get_db)
):
    """
    获取交易禁令列表
    
    @param skip: 跳过的记录数
    @param limit: 返回的记录数
    @param only_active: 是否只返回激活的禁令
    @param db: 数据库会话
    @returns: 交易禁令列表
    """
    trading_restrictions = crud.get_trading_restrictions(db, skip=skip, limit=limit, only_active=only_active)
    return trading_restrictions

@router.get("/{trading_restriction_id}", response_model=TradingRestriction)
def read_trading_restriction(
    trading_restriction_id: uuid.UUID = Path(..., description="交易禁令ID"),
    db: Session = Depends(get_db)
):
    """
    通过ID获取单个交易禁令
    
    @param trading_restriction_id: 交易禁令ID
    @param db: 数据库会话
    @returns: 交易禁令对象
    """
    db_trading_restriction = crud.get_trading_restriction(db, trading_restriction_id=trading_restriction_id)
    if db_trading_restriction is None:
        raise HTTPException(status_code=404, detail="交易禁令未找到")
    return db_trading_restriction

@router.put("/{trading_restriction_id}", response_model=TradingRestriction)
def update_trading_restriction(
    trading_restriction_id: uuid.UUID = Path(..., description="交易禁令ID"),
    trading_restriction: TradingRestrictionUpdate = None,
    db: Session = Depends(get_db)
):
    """
    更新交易禁令
    
    @param trading_restriction_id: 交易禁令ID
    @param trading_restriction: 交易禁令更新模式
    @param db: 数据库会话
    @returns: 更新后的交易禁令对象
    """
    db_trading_restriction = crud.update_trading_restriction(
        db, 
        trading_restriction_id=trading_restriction_id, 
        trading_restriction=trading_restriction
    )
    if db_trading_restriction is None:
        raise HTTPException(status_code=404, detail="交易禁令未找到")
    return db_trading_restriction

@router.delete("/{trading_restriction_id}", response_model=dict)
def delete_trading_restriction(
    trading_restriction_id: uuid.UUID = Path(..., description="交易禁令ID"),
    db: Session = Depends(get_db)
):
    """
    删除交易禁令
    
    @param trading_restriction_id: 交易禁令ID
    @param db: 数据库会话
    @returns: 删除结果
    """
    success = crud.delete_trading_restriction(db, trading_restriction_id=trading_restriction_id)
    if not success:
        raise HTTPException(status_code=404, detail="交易禁令未找到")
    return {"detail": "交易禁令已成功删除"}
