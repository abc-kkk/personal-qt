from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.database import engine, get_db, Base
from app.routers import categories, stock_trades, failure_cases, daily_reviews, upload

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="个人管理平台API",
    description="用于管理个人投资和生活记录的API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(categories.router)
app.include_router(stock_trades.router)
app.include_router(failure_cases.router)
app.include_router(daily_reviews.router)
app.include_router(upload.router)

@app.get("/")
def read_root():
    """
    API根路径
    
    @returns: 欢迎信息
    """
    return {"message": "欢迎使用个人管理平台API"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    健康检查
    
    @param db: 数据库会话
    @returns: 健康状态
    """
    try:
        # 尝试执行一个简单的数据库查询
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "ok",
        "database": db_status
    } 