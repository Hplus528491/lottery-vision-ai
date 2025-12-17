"""
認證工具模組

提供密碼加密、JWT 生成和驗證功能
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import User
from ..exceptions import AuthenticationError, ErrorCode


# 密碼加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    驗證密碼
    
    Args:
        plain_password: 明文密碼
        hashed_password: 加密密碼
        
    Returns:
        bool: 是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    加密密碼
    
    Args:
        password: 明文密碼
        
    Returns:
        str: 加密後的密碼
    """
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    創建訪問令牌
    
    Args:
        data: 令牌數據
        expires_delta: 過期時間
        
    Returns:
        str: JWT 令牌
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    創建刷新令牌
    
    Args:
        data: 令牌數據
        expires_delta: 過期時間
        
    Returns:
        str: JWT 令牌
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    解碼令牌
    
    Args:
        token: JWT 令牌
        
    Returns:
        dict: 令牌數據
        
    Raises:
        AuthenticationError: 令牌無效或過期
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise AuthenticationError(
            error_code=ErrorCode.TOKEN_INVALID,
            message="無效的令牌"
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    獲取當前用戶
    
    Args:
        token: JWT 令牌
        db: 資料庫會話
        
    Returns:
        User: 當前用戶
        
    Raises:
        AuthenticationError: 認證失敗
    """
    try:
        payload = decode_token(token)
        user_id: int = payload.get("sub")
        
        if user_id is None:
            raise AuthenticationError(
                error_code=ErrorCode.TOKEN_INVALID,
                message="無效的令牌"
            )
            
    except JWTError:
        raise AuthenticationError(
            error_code=ErrorCode.TOKEN_INVALID,
            message="無效的令牌"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise AuthenticationError(
            error_code=ErrorCode.USER_NOT_FOUND,
            message="用戶不存在"
        )
    
    if not user.is_active:
        raise AuthenticationError(
            error_code=ErrorCode.USER_INACTIVE,
            message="用戶已被停用"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    獲取當前活躍用戶
    
    Args:
        current_user: 當前用戶
        
    Returns:
        User: 當前活躍用戶
    """
    if not current_user.is_active:
        raise AuthenticationError(
            error_code=ErrorCode.USER_INACTIVE,
            message="用戶已被停用"
        )
    return current_user
