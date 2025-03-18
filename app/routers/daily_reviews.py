from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import date

from app.database.database import get_db
from app.database import crud
from app.schemas.daily_review import DailyReview, DailyReviewCreate, DailyReviewUpdate

router = APIRouter(
    prefix="/daily-reviews",
    tags=["daily_reviews"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=DailyReview, status_code=status.HTTP_201_CREATED)
def create_daily_review(daily_review: DailyReviewCreate, db: Session = Depends(get_db)):
    """
    创建新每日复盘
    
    @param daily_review: 每日复盘创建模式
    @param db: 数据库会话
    @returns: 创建的每日复盘
    @raises: 400 如果该日期已存在复盘记录
    """
    # 检查该日期是否已存在复盘记录
    existing_review = crud.get_daily_review_by_date(db, review_date=daily_review.review_date)
    if existing_review:
        raise HTTPException(status_code=400, detail="该日期已存在复盘记录")
    
    return crud.create_daily_review(db=db, daily_review=daily_review)

@router.get("/", response_model=List[DailyReview])
def read_daily_reviews(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取每日复盘列表
    
    @param skip: 跳过的记录数
    @param limit: 返回的最大记录数
    @param db: 数据库会话
    @returns: 每日复盘列表
    """
    daily_reviews = crud.get_daily_reviews(db, skip=skip, limit=limit)
    return daily_reviews

@router.get("/by-date/{review_date}", response_model=DailyReview)
def read_daily_review_by_date(review_date: date, db: Session = Depends(get_db)):
    """
    通过日期获取每日复盘
    
    @param review_date: 复盘日期
    @param db: 数据库会话
    @returns: 每日复盘
    @raises: 404 如果该日期的复盘不存在
    """
    db_daily_review = crud.get_daily_review_by_date(db, review_date=review_date)
    if db_daily_review is None:
        raise HTTPException(status_code=404, detail="该日期的复盘不存在")
    return db_daily_review

@router.get("/{daily_review_id}", response_model=DailyReview)
def read_daily_review(daily_review_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    通过ID获取每日复盘
    
    @param daily_review_id: 每日复盘ID
    @param db: 数据库会话
    @returns: 每日复盘
    @raises: 404 如果每日复盘不存在
    """
    db_daily_review = crud.get_daily_review(db, daily_review_id=daily_review_id)
    if db_daily_review is None:
        raise HTTPException(status_code=404, detail="每日复盘不存在")
    return db_daily_review

@router.put("/{daily_review_id}", response_model=DailyReview)
def update_daily_review(daily_review_id: uuid.UUID, daily_review: DailyReviewUpdate, db: Session = Depends(get_db)):
    """
    更新每日复盘
    
    @param daily_review_id: 每日复盘ID
    @param daily_review: 每日复盘更新模式
    @param db: 数据库会话
    @returns: 更新后的每日复盘
    @raises: 404 如果每日复盘不存在
    @raises: 400 如果更新后的日期与其他复盘记录冲突
    """
    # 检查复盘记录是否存在
    db_daily_review = crud.get_daily_review(db, daily_review_id=daily_review_id)
    if db_daily_review is None:
        raise HTTPException(status_code=404, detail="每日复盘不存在")
    
    # 如果更新了日期，检查新日期是否与其他记录冲突
    if daily_review.review_date and daily_review.review_date != db_daily_review.review_date:
        existing_review = crud.get_daily_review_by_date(db, review_date=daily_review.review_date)
        if existing_review and existing_review.id != daily_review_id:
            raise HTTPException(status_code=400, detail="该日期已存在其他复盘记录")
    
    # 更新复盘记录
    db_daily_review = crud.update_daily_review(db, daily_review_id=daily_review_id, daily_review=daily_review)
    return db_daily_review

@router.delete("/{daily_review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_daily_review(daily_review_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    删除每日复盘
    
    @param daily_review_id: 每日复盘ID
    @param db: 数据库会话
    @raises: 404 如果每日复盘不存在
    """
    db_daily_review = crud.get_daily_review(db, daily_review_id=daily_review_id)
    if db_daily_review is None:
        raise HTTPException(status_code=404, detail="每日复盘不存在")
    
    crud.delete_daily_review(db, daily_review_id=daily_review_id) 