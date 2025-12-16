"""
API Schemas 模組

定義所有 API 請求和響應的數據結構
"""

from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, EmailStr, Field


# ==================== 通用 Schemas ====================

class ResponseBase(BaseModel):
    """通用響應基類"""
    success: bool = True
    message: Optional[str] = None


class PaginationParams(BaseModel):
    """分頁參數"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(ResponseBase):
    """分頁響應基類"""
    total: int
    page: int
    page_size: int
    total_pages: int


# ==================== 用戶 Schemas ====================

class UserBase(BaseModel):
    """用戶基類"""
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)


class UserCreate(UserBase):
    """用戶創建請求"""
    password: str = Field(min_length=8, max_length=100)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """用戶登入請求"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """用戶更新請求"""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    """用戶響應"""
    id: int
    full_name: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    is_verified: bool
    credits: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token 響應"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthResponse(ResponseBase):
    """認證響應"""
    user: UserResponse
    token: TokenResponse


# ==================== 彩券 Schemas ====================

class LotteryDrawBase(BaseModel):
    """彩券開獎基類"""
    lottery_type: str
    draw_number: str
    draw_date: datetime
    numbers: List[int]
    special_number: Optional[int] = None


class LotteryDrawCreate(LotteryDrawBase):
    """彩券開獎創建請求"""
    prize_info: Optional[dict] = None
    total_sales: Optional[int] = None


class LotteryDrawResponse(LotteryDrawBase):
    """彩券開獎響應"""
    id: int
    prize_info: Optional[dict]
    total_sales: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class LotteryDrawListResponse(PaginatedResponse):
    """彩券開獎列表響應"""
    data: List[LotteryDrawResponse]


class LotteryStatisticsResponse(BaseModel):
    """彩券統計響應"""
    lottery_type: str
    number: int
    frequency: int
    last_appeared: Optional[datetime]
    average_interval: Optional[int]
    max_interval: Optional[int]
    current_interval: int
    
    class Config:
        from_attributes = True


# ==================== 推薦 Schemas ====================

class RecommendationRequest(BaseModel):
    """推薦請求"""
    lottery_type: str
    strategy: Optional[str] = "balanced"
    count: int = Field(default=1, ge=1, le=10)


class RecommendationResponse(BaseModel):
    """推薦響應"""
    id: int
    lottery_type: str
    recommended_numbers: List[int]
    special_number: Optional[int]
    analysis: Optional[str]
    confidence_score: Optional[float]
    strategy: Optional[str]
    credits_used: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class RecommendationListResponse(PaginatedResponse):
    """推薦列表響應"""
    data: List[RecommendationResponse]


# ==================== 積分 Schemas ====================

class CreditBalanceResponse(ResponseBase):
    """積分餘額響應"""
    credits: int
    user_id: int


class CreditTransactionResponse(BaseModel):
    """積分交易響應"""
    id: int
    transaction_type: str
    amount: int
    balance_before: int
    balance_after: int
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class CreditTransactionListResponse(PaginatedResponse):
    """積分交易列表響應"""
    data: List[CreditTransactionResponse]


class CreditPackageResponse(BaseModel):
    """積分套餐響應"""
    id: int
    name: str
    description: Optional[str]
    credits: int
    price: int
    bonus_credits: int
    
    class Config:
        from_attributes = True


class CreditPackageListResponse(ResponseBase):
    """積分套餐列表響應"""
    data: List[CreditPackageResponse]


# ==================== 統計 Schemas ====================

class NumberFrequencyResponse(BaseModel):
    """號碼頻率響應"""
    number: int
    frequency: int
    percentage: float


class LotteryAnalysisResponse(ResponseBase):
    """彩券分析響應"""
    lottery_type: str
    total_draws: int
    hot_numbers: List[NumberFrequencyResponse]
    cold_numbers: List[NumberFrequencyResponse]
    overdue_numbers: List[int]
    recent_numbers: List[List[int]]
