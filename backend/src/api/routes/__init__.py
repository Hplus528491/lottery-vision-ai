"""
API 路由模組

導出所有 API 路由
"""

from .auth import router as auth_router
from .lottery import router as lottery_router
from .recommendation import router as recommendation_router
from .credits import router as credits_router

__all__ = [
    "auth_router",
    "lottery_router",
    "recommendation_router",
    "credits_router"
]
