"""
應用配置模組

管理所有環境變數和應用配置
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


def get_database_url() -> str:
    """獲取並修正數據庫連接字符串"""
    database_url = os.getenv("DATABASE_URL", "")
    
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")
    
    # Railway 的 Postgres 使用 postgres:// 開頭，需要轉換為 postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif database_url.startswith("postgresql://"):
        # 確保使用 psycopg2 driver
        database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    return database_url


class Settings(BaseSettings):
    """應用配置類"""
    
    # 應用基本配置
    APP_NAME: str = "LotteryVisionAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 資料庫配置
    DATABASE_URL: str = get_database_url()  # 從環境變量讀取並自動轉換格式
    
    # DATABASE_URL: str  # 從環境變量讀取，無默認值
    
    # JWT 配置
    
    # JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-min-32-characters-long-for-security")
    # JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    # JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    # JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    JWT_SECRET_KEY: str = "your-secret-key-min-32-characters-long-for-security"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    
    # Manus API 配置
    MANUS_API_KEY: Optional[str] = None
    MANUS_API_BASE_URL: str = "https://api.manus.ai/v1"
    
    # 前端配置
    FRONTEND_URL: str = "http://localhost:3000"
    
    # CORS 配置
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # 虛擬積分配置
    INITIAL_CREDITS: int = 100
    RECOMMENDATION_COST: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# @lru_cache()
def get_settings() -> Settings:
    """
    獲取應用配置 (使用緩存)
    
    Returns:
        Settings: 應用配置實例
    """
    return Settings()


# 導出配置實例
settings = get_settings()
