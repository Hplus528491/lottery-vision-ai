"""
認證 API 路由

處理用戶註冊、登入、登出等認證相關請求
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import User
from ...config import settings
from ...exceptions import AuthenticationError, ErrorCode, AppException
from ...utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user
)
from ..schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    AuthResponse,
    ResponseBase
)


router = APIRouter(prefix="/auth", tags=["認證"])


@router.post("/register", response_model=AuthResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    用戶註冊
    
    創建新用戶帳戶並返回認證令牌
    """
    # 檢查郵箱是否已存在
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise AppException(
            error_code=ErrorCode.EMAIL_ALREADY_EXISTS,
            message="該郵箱已被註冊",
            status_code=400
        )
    
    # 檢查用戶名是否已存在
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise AppException(
            error_code=ErrorCode.USERNAME_ALREADY_EXISTS,
            message="該用戶名已被使用",
            status_code=400
        )
    
    # 創建新用戶
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        credits=settings.INITIAL_CREDITS
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 創建令牌
    access_token = create_access_token(data={"sub": new_user.id})
    refresh_token = create_refresh_token(data={"sub": new_user.id})
    
    return AuthResponse(
        success=True,
        message="註冊成功",
        user=UserResponse.model_validate(new_user),
        token=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    用戶登入
    
    驗證用戶憑證並返回認證令牌
    """
    # 查找用戶
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise AuthenticationError(
            error_code=ErrorCode.INVALID_CREDENTIALS,
            message="郵箱或密碼錯誤"
        )
    
    if not user.is_active:
        raise AuthenticationError(
            error_code=ErrorCode.USER_INACTIVE,
            message="帳戶已被停用"
        )
    
    # 更新最後登入時間
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # 創建令牌
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return AuthResponse(
        success=True,
        message="登入成功",
        user=UserResponse.model_validate(user),
        token=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    刷新令牌
    
    使用刷新令牌獲取新的訪問令牌
    """
    try:
        payload = decode_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise AuthenticationError(
                error_code=ErrorCode.TOKEN_INVALID,
                message="無效的刷新令牌"
            )
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise AuthenticationError(
                error_code=ErrorCode.USER_NOT_FOUND,
                message="用戶不存在或已被停用"
            )
        
        # 創建新令牌
        new_access_token = create_access_token(data={"sub": user.id})
        new_refresh_token = create_refresh_token(data={"sub": user.id})
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception:
        raise AuthenticationError(
            error_code=ErrorCode.TOKEN_INVALID,
            message="無效的刷新令牌"
        )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    獲取當前用戶信息
    """
    return UserResponse.model_validate(current_user)


@router.post("/logout", response_model=ResponseBase)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    用戶登出
    
    注意: JWT 是無狀態的，這裡只是返回成功響應
    實際的令牌失效需要在前端清除令牌
    """
    return ResponseBase(
        success=True,
        message="登出成功"
    )
