"""
API 模組

導出所有 API 路由和 Schemas
"""

from .routes import (
    auth_router,
    lottery_router,
    recommendation_router,
    credits_router,
    debug_router  # ⚠️ 臨時調試路由
)

from .schemas import (
    # 通用
    ResponseBase,
    PaginationParams,
    PaginatedResponse,
    
    # 用戶
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    TokenResponse,
    AuthResponse,
    
    # 彩券
    LotteryDrawCreate,
    LotteryDrawResponse,
    LotteryDrawListResponse,
    LotteryStatisticsResponse,
    LotteryAnalysisResponse,
    NumberFrequencyResponse,
    
    # 推薦
    RecommendationRequest,
    RecommendationResponse,
    RecommendationListResponse,
    
    # 積分
    CreditBalanceResponse,
    CreditTransactionResponse,
    CreditTransactionListResponse,
    CreditPackageResponse,
    CreditPackageListResponse
)

__all__ = [
    # 路由
    "auth_router",
    "lottery_router",
    "recommendation_router",
    "credits_router",
    "debug_router",  # ⚠️ 臨時調試路由
    
    # Schemas
    "ResponseBase",
    "PaginationParams",
    "PaginatedResponse",
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "TokenResponse",
    "AuthResponse",
    "LotteryDrawCreate",
    "LotteryDrawResponse",
    "LotteryDrawListResponse",
    "LotteryStatisticsResponse",
    "LotteryAnalysisResponse",
    "NumberFrequencyResponse",
    "RecommendationRequest",
    "RecommendationResponse",
    "RecommendationListResponse",
    "CreditBalanceResponse",
    "CreditTransactionResponse",
    "CreditTransactionListResponse",
    "CreditPackageResponse",
    "CreditPackageListResponse"
]
