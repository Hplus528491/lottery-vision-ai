"""
臨時調試路由 - 用於檢查環境變量和配置

⚠️ 警告：此文件僅用於調試，完成後請立即刪除！
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
import os

from ...config import settings

router = APIRouter(prefix="/debug", tags=["Debug"])


@router.get("/config")
async def debug_config() -> Dict[str, Any]:
    """
    顯示當前配置信息（僅顯示部分信息以保護安全）
    
    ⚠️ 調試完成後請刪除此端點！
    """
    return {
        "message": "⚠️ 這是臨時調試端點，請在調試完成後刪除！",
        "config": {
            "APP_NAME": settings.APP_NAME,
            "APP_VERSION": settings.APP_VERSION,
            "DEBUG": settings.DEBUG,
            
            # JWT 配置
            "JWT_SECRET_KEY_PREFIX": settings.JWT_SECRET_KEY[:20],
            "JWT_SECRET_KEY_SUFFIX": settings.JWT_SECRET_KEY[-10:],
            "JWT_SECRET_KEY_LENGTH": len(settings.JWT_SECRET_KEY),
            "JWT_ALGORITHM": settings.JWT_ALGORITHM,
            "ACCESS_TOKEN_EXPIRE_MINUTES": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            "REFRESH_TOKEN_EXPIRE_DAYS": settings.REFRESH_TOKEN_EXPIRE_DAYS,
            
            # Manus API 配置
            "MANUS_API_KEY_SET": settings.MANUS_API_KEY is not None,
            "MANUS_API_KEY_PREFIX": settings.MANUS_API_KEY[:20] if settings.MANUS_API_KEY else None,
            "MANUS_API_KEY_LENGTH": len(settings.MANUS_API_KEY) if settings.MANUS_API_KEY else 0,
            "MANUS_API_BASE_URL": settings.MANUS_API_BASE_URL,
            
            # 數據庫配置
            "DATABASE_URL_PREFIX": settings.DATABASE_URL[:40] if settings.DATABASE_URL else None,
        }
    }


@router.get("/env")
async def debug_env() -> Dict[str, Any]:
    """
    顯示環境變量信息（僅顯示部分信息以保護安全）
    
    ⚠️ 調試完成後請刪除此端點！
    """
    jwt_secret_key = os.getenv("JWT_SECRET_KEY", "")
    manus_api_key = os.getenv("MANUS_API_KEY", "")
    
    return {
        "message": "⚠️ 這是臨時調試端點，請在調試完成後刪除！",
        "environment_variables": {
            # JWT 相關
            "JWT_SECRET_KEY_SET": bool(jwt_secret_key),
            "JWT_SECRET_KEY_PREFIX": jwt_secret_key[:20] if jwt_secret_key else None,
            "JWT_SECRET_KEY_SUFFIX": jwt_secret_key[-10:] if jwt_secret_key else None,
            "JWT_SECRET_KEY_LENGTH": len(jwt_secret_key),
            "JWT_SECRET_KEY_HAS_SPACES": " " in jwt_secret_key,
            "JWT_SECRET_KEY_HAS_NEWLINES": "\n" in jwt_secret_key or "\r" in jwt_secret_key,
            
            "JWT_ALGORITHM": os.getenv("JWT_ALGORITHM"),
            "ACCESS_TOKEN_EXPIRE_MINUTES": os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"),
            "REFRESH_TOKEN_EXPIRE_DAYS": os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"),
            
            # Manus API 相關
            "MANUS_API_KEY_SET": bool(manus_api_key),
            "MANUS_API_KEY_PREFIX": manus_api_key[:20] if manus_api_key else None,
            "MANUS_API_KEY_LENGTH": len(manus_api_key),
            "MANUS_API_BASE_URL": os.getenv("MANUS_API_BASE_URL"),
            
            # 數據庫相關
            "DATABASE_URL_SET": bool(os.getenv("DATABASE_URL")),
            "DATABASE_URL_PREFIX": os.getenv("DATABASE_URL", "")[:40] if os.getenv("DATABASE_URL") else None,
        }
    }


@router.get("/comparison")
async def debug_comparison() -> Dict[str, Any]:
    """
    對比 settings 和環境變量中的配置
    
    ⚠️ 調試完成後請刪除此端點！
    """
    env_jwt_secret = os.getenv("JWT_SECRET_KEY", "")
    settings_jwt_secret = settings.JWT_SECRET_KEY
    
    return {
        "message": "⚠️ 這是臨時調試端點，請在調試完成後刪除！",
        "comparison": {
            "jwt_secret_key": {
                "from_env_prefix": env_jwt_secret[:20],
                "from_env_suffix": env_jwt_secret[-10:],
                "from_env_length": len(env_jwt_secret),
                
                "from_settings_prefix": settings_jwt_secret[:20],
                "from_settings_suffix": settings_jwt_secret[-10:],
                "from_settings_length": len(settings_jwt_secret),
                
                "are_equal": env_jwt_secret == settings_jwt_secret,
                "length_match": len(env_jwt_secret) == len(settings_jwt_secret),
            },
            "manus_api_key": {
                "from_env_set": bool(os.getenv("MANUS_API_KEY")),
                "from_settings_set": settings.MANUS_API_KEY is not None,
                "are_equal": os.getenv("MANUS_API_KEY") == settings.MANUS_API_KEY,
            }
        }
    }


@router.get("/jwt-test")
async def debug_jwt_test() -> Dict[str, Any]:
    """
    測試 JWT Token 生成和驗證
    
    ⚠️ 調試完成後請刪除此端點！
    """
    from jose import jwt
    from datetime import datetime, timedelta
    
    # 測試數據
    test_data = {"sub": 999, "test": True}
    
    # 使用 settings 中的密鑰生成 Token
    test_token = jwt.encode(
        {**test_data, "exp": datetime.utcnow() + timedelta(minutes=5)},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    # 嘗試驗證 Token
    try:
        decoded = jwt.decode(
            test_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        verification_success = True
        verification_error = None
    except Exception as e:
        verification_success = False
        verification_error = str(e)
        decoded = None
    
    return {
        "message": "⚠️ 這是臨時調試端點，請在調試完成後刪除！",
        "test_result": {
            "test_token_generated": test_token[:50] + "...",
            "test_token_length": len(test_token),
            "verification_success": verification_success,
            "verification_error": verification_error,
            "decoded_payload": decoded,
            
            "jwt_secret_key_used": {
                "prefix": settings.JWT_SECRET_KEY[:20],
                "suffix": settings.JWT_SECRET_KEY[-10:],
                "length": len(settings.JWT_SECRET_KEY),
            }
        }
    }
