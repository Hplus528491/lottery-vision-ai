"""
資料庫連接模組

管理 PostgreSQL 資料庫連接和會話
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from ..config import settings


# 創建資料庫引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG
)

# 創建會話工廠
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 創建基礎模型類
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    獲取資料庫會話
    
    Yields:
        Session: 資料庫會話
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    初始化資料庫
    
    創建所有表格
    """
    # 導入所有模型以確保它們被註冊
    from ..models import user, lottery, recommendation, credit
    
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    刪除所有資料庫表格
    
    警告: 這會刪除所有數據！
    """
    Base.metadata.drop_all(bind=engine)
