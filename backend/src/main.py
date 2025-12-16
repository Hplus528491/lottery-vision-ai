"""
LotteryVisionAI - FastAPI 主應用

AI 驅動的彩券號碼推薦平台
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from .config import settings
from .database import init_db, engine, Base
from .exceptions import AppException, app_exception_handler, general_exception_handler
from .api import (
    auth_router,
    lottery_router,
    recommendation_router,
    credits_router
)


# 配置日誌
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    應用生命週期管理
    
    在應用啟動時初始化資料庫，在關閉時清理資源
    """
    # 啟動時
    logger.info("🚀 LotteryVisionAI 正在啟動...")
    
    try:
        # 初始化資料庫
        init_db()
        logger.info("✅ 資料庫初始化完成")
    except Exception as e:
        logger.error(f"❌ 資料庫初始化失敗: {e}")
    
    logger.info("✅ LotteryVisionAI 啟動完成！")
    
    yield
    
    # 關閉時
    logger.info("👋 LotteryVisionAI 正在關閉...")


# 創建 FastAPI 應用
app = FastAPI(
    title="LotteryVisionAI",
    description="""
    🎰 **LotteryVisionAI** - AI 驅動的彩券號碼推薦平台
    
    ## 功能特點
    
    - 🤖 **AI 智慧推薦**: 使用 Claude AI 分析歷史數據，生成智慧推薦號碼
    - 📊 **統計分析**: 提供詳細的號碼統計和分析報告
    - 💰 **虛擬積分**: 使用積分系統管理推薦服務
    - 🔐 **安全認證**: JWT 認證保護用戶數據
    
    ## 支持的彩券類型
    
    - 大樂透
    - 威力彩
    - 今彩539
    - 雙贏彩
    
    ## API 版本
    
    當前版本: v1
    """,
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# 設置調試模式
app.debug = settings.DEBUG


# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 註冊異常處理器
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# 註冊 API 路由
API_PREFIX = "/api/v1"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(lottery_router, prefix=API_PREFIX)
app.include_router(recommendation_router, prefix=API_PREFIX)
app.include_router(credits_router, prefix=API_PREFIX)


# 健康檢查端點
@app.get("/health", tags=["系統"])
async def health_check():
    """
    健康檢查
    
    返回應用運行狀態
    """
    return {
        "status": "healthy",
        "app": "LotteryVisionAI",
        "version": "1.0.0"
    }


@app.get("/", tags=["系統"])
async def root():
    """
    根端點
    
    返回歡迎信息和 API 文檔鏈接
    """
    return {
        "message": "歡迎使用 LotteryVisionAI API",
        "docs": "/docs" if settings.DEBUG else "API 文檔已禁用",
        "health": "/health"
    }


# 開發環境入口
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
