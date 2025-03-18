from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database.database import get_db
from app.database import crud
from app.schemas.category import Category, CategoryCreate, CategoryUpdate

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """
    创建新分类
    
    @param category: 分类创建模式
    @param db: 数据库会话
    @returns: 创建的分类
    """
    return crud.create_category(db=db, category=category)

@router.get("/", response_model=List[Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取分类列表
    
    @param skip: 跳过的记录数
    @param limit: 返回的最大记录数
    @param db: 数据库会话
    @returns: 分类列表
    """
    categories = crud.get_categories(db, skip=skip, limit=limit)
    return categories

@router.get("/{category_id}", response_model=Category)
def read_category(category_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    通过ID获取分类
    
    @param category_id: 分类ID
    @param db: 数据库会话
    @returns: 分类
    @raises: 404 如果分类不存在
    """
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    return db_category

@router.put("/{category_id}", response_model=Category)
def update_category(category_id: uuid.UUID, category: CategoryUpdate, db: Session = Depends(get_db)):
    """
    更新分类
    
    @param category_id: 分类ID
    @param category: 分类更新模式
    @param db: 数据库会话
    @returns: 更新后的分类
    @raises: 404 如果分类不存在
    """
    db_category = crud.update_category(db, category_id=category_id, category=category)
    if db_category is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    return db_category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    删除分类
    
    @param category_id: 分类ID
    @param db: 数据库会话
    @raises: 404 如果分类不存在
    @raises: 400 如果分类有关联的交易记录
    """
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    result = crud.delete_category(db, category_id=category_id)
    if not result:
        raise HTTPException(status_code=400, detail="无法删除分类，该分类下有关联的交易记录") 