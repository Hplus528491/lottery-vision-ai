"""
應用配置模組

管理所有環境變數和應用配置
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """應用配置類"""
    
    # 應用基本配置
    APP_NAME: str = "LotteryVisionAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 資料庫配置
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/lottery"
    
    # JWT 配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
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


@lru_cache()
def get_settings() -> Settings:
    """
    獲取應用配置 (使用緩存)
    
    Returns:
        Settings: 應用配置實例
    """
    return Settings()


# 導出配置實例
settings = get_settings()
