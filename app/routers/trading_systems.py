from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.database.database import get_db
from app.database import crud
from app.schemas.trading_system import TradingSystem, TradingSystemCreate, TradingSystemUpdate

router = APIRouter(
    prefix="/trading-systems",
    tags=["交易系统"],
    responses={404: {"description": "资源未找到"}},
)

@router.post("/", response_model=TradingSystem)
def create_trading_system(
    trading_system: TradingSystemCreate,
    db: Session = Depends(get_db)
):
    """
    创建交易系统
    
    @param trading_system: 交易系统创建模式
    @param db: 数据库会话
    @returns: 创建的交易系统对象
    """
    return crud.create_trading_system(db=db, trading_system=trading_system)

@router.get("/", response_model=List[TradingSystem])
def read_trading_systems(
    skip: int = Query(0, description="跳过的记录数"),
    limit: int = Query(100, description="返回的记录数"),
    only_active: bool = Query(False, description="是否只返回激活的系统"),
    db: Session = Depends(get_db)
):
    """
    获取交易系统列表
    
    @param skip: 跳过的记录数
    @param limit: 返回的记录数
    @param only_active: 是否只返回激活的系统
    @param db: 数据库会话
    @returns: 交易系统列表
    """
    trading_systems = crud.get_trading_systems(db, skip=skip, limit=limit, only_active=only_active)
    return trading_systems

@router.get("/{trading_system_id}", response_model=TradingSystem)
def read_trading_system(
    trading_system_id: uuid.UUID = Path(..., description="交易系统ID"),
    db: Session = Depends(get_db)
):
    """
    通过ID获取单个交易系统
    
    @param trading_system_id: 交易系统ID
    @param db: 数据库会话
    @returns: 交易系统对象
    """
    db_trading_system = crud.get_trading_system(db, trading_system_id=trading_system_id)
    if db_trading_system is None:
        raise HTTPException(status_code=404, detail="交易系统未找到")
    return db_trading_system

@router.put("/{trading_system_id}", response_model=TradingSystem)
def update_trading_system(
    trading_system_id: uuid.UUID = Path(..., description="交易系统ID"),
    trading_system: TradingSystemUpdate = None,
    db: Session = Depends(get_db)
):
    """
    更新交易系统
    
    @param trading_system_id: 交易系统ID
    @param trading_system: 交易系统更新模式
    @param db: 数据库会话
    @returns: 更新后的交易系统对象
    """
    db_trading_system = crud.update_trading_system(db, trading_system_id=trading_system_id, trading_system=trading_system)
    if db_trading_system is None:
        raise HTTPException(status_code=404, detail="交易系统未找到")
    return db_trading_system

@router.delete("/{trading_system_id}", response_model=dict)
def delete_trading_system(
    trading_system_id: uuid.UUID = Path(..., description="交易系统ID"),
    db: Session = Depends(get_db)
):
    """
    删除交易系统
    
    @param trading_system_id: 交易系统ID
    @param db: 数据库会话
    @returns: 删除结果
    """
    success = crud.delete_trading_system(db, trading_system_id=trading_system_id)
    if not success:
        raise HTTPException(status_code=404, detail="交易系统未找到")
    return {"detail": "交易系统已成功删除"}
