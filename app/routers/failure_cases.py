from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database.database import get_db
from app.database import crud
from app.schemas.failure_case import FailureCase, FailureCaseCreate, FailureCaseUpdate

router = APIRouter(
    prefix="/failure-cases",
    tags=["failure_cases"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=FailureCase, status_code=status.HTTP_201_CREATED)
def create_failure_case(failure_case: FailureCaseCreate, db: Session = Depends(get_db)):
    """
    创建新失败案例
    
    @param failure_case: 失败案例创建模式
    @param db: 数据库会话
    @returns: 创建的失败案例
    """
    return crud.create_failure_case(db=db, failure_case=failure_case)

@router.get("/", response_model=List[FailureCase])
def read_failure_cases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取失败案例列表
    
    @param skip: 跳过的记录数
    @param limit: 返回的最大记录数
    @param db: 数据库会话
    @returns: 失败案例列表
    """
    failure_cases = crud.get_failure_cases(db, skip=skip, limit=limit)
    return failure_cases

@router.get("/{failure_case_id}", response_model=FailureCase)
def read_failure_case(failure_case_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    通过ID获取失败案例
    
    @param failure_case_id: 失败案例ID
    @param db: 数据库会话
    @returns: 失败案例
    @raises: 404 如果失败案例不存在
    """
    db_failure_case = crud.get_failure_case(db, failure_case_id=failure_case_id)
    if db_failure_case is None:
        raise HTTPException(status_code=404, detail="失败案例不存在")
    return db_failure_case

@router.put("/{failure_case_id}", response_model=FailureCase)
def update_failure_case(failure_case_id: uuid.UUID, failure_case: FailureCaseUpdate, db: Session = Depends(get_db)):
    """
    更新失败案例
    
    @param failure_case_id: 失败案例ID
    @param failure_case: 失败案例更新模式
    @param db: 数据库会话
    @returns: 更新后的失败案例
    @raises: 404 如果失败案例不存在
    """
    db_failure_case = crud.update_failure_case(db, failure_case_id=failure_case_id, failure_case=failure_case)
    if db_failure_case is None:
        raise HTTPException(status_code=404, detail="失败案例不存在")
    return db_failure_case

@router.delete("/{failure_case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_failure_case(failure_case_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    删除失败案例
    
    @param failure_case_id: 失败案例ID
    @param db: 数据库会话
    @raises: 404 如果失败案例不存在
    """
    db_failure_case = crud.get_failure_case(db, failure_case_id=failure_case_id)
    if db_failure_case is None:
        raise HTTPException(status_code=404, detail="失败案例不存在")
    
    crud.delete_failure_case(db, failure_case_id=failure_case_id) 