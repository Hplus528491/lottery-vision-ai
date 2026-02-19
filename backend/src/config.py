"""
應用配置模組

管理所有環境變數和應用配置
"""

import os
from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """應用配置類"""
    
    # 應用基本配置
    APP_NAME: str = "LotteryVisionAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 資料庫配置 (必須從環境變量讀取)
    DATABASE_URL: str
    
    # JWT 配置 (必須從環境變量讀取,無默認值)
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
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
    
    @field_validator("DATABASE_URL")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        """
        修正數據庫連接字符串
        Railway 的 Postgres 使用 postgres:// 開頭，需要轉換為 postgresql+psycopg2://
        """
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+psycopg2://", 1)
        elif v.startswith("postgresql://") and "psycopg2" not in v:
            return v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v
    
    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """驗證 JWT 密鑰長度"""
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY 必須至少 32 個字符")
        return v
    
    # JWT 相關屬性別名 (兼容舊代碼)
    @property
    def JWT_ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        return self.ACCESS_TOKEN_EXPIRE_MINUTES
    
    @property
    def JWT_REFRESH_TOKEN_EXPIRE_DAYS(self) -> int:
        return self.REFRESH_TOKEN_EXPIRE_DAYS
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # 允許使用 @property
        arbitrary_types_allowed = True


@lru_cache()
def get_settings() -> Settings:
    """
    獲取應用配置 (使用緩存)
    
    Returns:
        Settings: 應用配置實例
    """
    settings_instance = Settings()
    
    # 啟動時輸出關鍵配置 (僅顯示前10個字符,避免洩漏)
    print("=" * 50)
    print("🔧 Configuration Loaded")
    print("=" * 50)
    print(f"APP_NAME: {settings_instance.APP_NAME}")
    print(f"DATABASE_URL: {settings_instance.DATABASE_URL[:30]}...")
    print(f"JWT_SECRET_KEY: {settings_instance.JWT_SECRET_KEY[:10]}... (length: {len(settings_instance.JWT_SECRET_KEY)})")
    print(f"JWT_ALGORITHM: {settings_instance.JWT_ALGORITHM}")
    print(f"MANUS_API_KEY: {'✅ Set' if settings_instance.MANUS_API_KEY else '❌ Not Set'}")
    print("=" * 50)
    
    return settings_instance


# 導出配置實例
settings = get_settings()
