from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库连接字符串
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_h8KBVJEez9sF@ep-shrill-bar-a5euz3sp-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require")

# 创建数据库引擎
engine = create_engine(DATABASE_URL)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

# 获取数据库会话
def get_db():
    """
    获取数据库会话的依赖函数
    
    @returns: 数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 