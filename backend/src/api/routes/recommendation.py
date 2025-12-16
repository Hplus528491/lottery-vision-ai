"""
推薦 API 路由

處理 AI 推薦號碼生成和查詢
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ...database import get_db
from ...models import User, Recommendation, CreditTransaction, LotteryStatistics
from ...config import settings
from ...exceptions import InsufficientCreditsError, NotFoundError, ErrorCode, AppException
from ...utils import get_current_user
from ..schemas import (
    RecommendationRequest,
    RecommendationResponse,
    RecommendationListResponse,
    ResponseBase
)
from ...analyzer.ai_recommender import AIRecommender


router = APIRouter(prefix="/recommendations", tags=["推薦"])


@router.post("", response_model=RecommendationResponse)
async def create_recommendation(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成 AI 推薦號碼
    
    消耗用戶積分，使用 AI 分析生成推薦號碼
    """
    # 計算所需積分
    credits_needed = settings.RECOMMENDATION_COST * request.count
    
    # 檢查積分是否足夠
    if current_user.credits < credits_needed:
        raise InsufficientCreditsError(
            message="積分不足，無法生成推薦",
            required=credits_needed,
            available=current_user.credits
        )
    
    # 獲取統計數據
    stats = db.query(LotteryStatistics) \
        .filter(LotteryStatistics.lottery_type == request.lottery_type) \
        .all()
    
    # 使用 AI 推薦器生成號碼
    recommender = AIRecommender(db)
    recommendation_result = await recommender.generate_recommendation(
        lottery_type=request.lottery_type,
        strategy=request.strategy,
        statistics=stats
    )
    
    # 扣除積分
    balance_before = current_user.credits
    current_user.credits -= credits_needed
    balance_after = current_user.credits
    
    # 記錄積分交易
    transaction = CreditTransaction(
        user_id=current_user.id,
        transaction_type="recommendation",
        amount=-credits_needed,
        balance_before=balance_before,
        balance_after=balance_after,
        description=f"生成 {request.lottery_type} 推薦號碼",
        reference_type="recommendation"
    )
    db.add(transaction)
    
    # 創建推薦記錄
    recommendation = Recommendation(
        user_id=current_user.id,
        lottery_type=request.lottery_type,
        recommended_numbers=recommendation_result["numbers"],
        special_number=recommendation_result.get("special_number"),
        analysis=recommendation_result.get("analysis"),
        confidence_score=recommendation_result.get("confidence_score"),
        strategy=request.strategy,
        credits_used=credits_needed,
        statistics_basis=recommendation_result.get("statistics_basis")
    )
    db.add(recommendation)
    
    # 更新交易關聯
    db.commit()
    db.refresh(recommendation)
    
    transaction.reference_id = recommendation.id
    db.commit()
    
    return RecommendationResponse.model_validate(recommendation)


@router.get("", response_model=RecommendationListResponse)
async def get_recommendations(
    lottery_type: Optional[str] = Query(None, description="彩券類型"),
    page: int = Query(1, ge=1, description="頁碼"),
    page_size: int = Query(20, ge=1, le=100, description="每頁數量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    獲取用戶的推薦記錄
    """
    query = db.query(Recommendation).filter(Recommendation.user_id == current_user.id)
    
    if lottery_type:
        query = query.filter(Recommendation.lottery_type == lottery_type)
    
    # 計算總數
    total = query.count()
    
    # 分頁
    recommendations = query.order_by(desc(Recommendation.created_at)) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()
    
    return RecommendationListResponse(
        success=True,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
        data=[RecommendationResponse.model_validate(r) for r in recommendations]
    )


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
async def get_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    獲取單個推薦記錄
    """
    recommendation = db.query(Recommendation) \
        .filter(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == current_user.id
        ) \
        .first()
    
    if not recommendation:
        raise NotFoundError(
            error_code=ErrorCode.NOT_FOUND,
            message="推薦記錄不存在"
        )
    
    return RecommendationResponse.model_validate(recommendation)


@router.get("/strategies/list", response_model=ResponseBase)
async def get_strategies():
    """
    獲取可用的推薦策略
    """
    strategies = [
        {
            "id": "balanced",
            "name": "平衡策略",
            "description": "綜合考慮熱門號碼和冷門號碼，平衡選擇"
        },
        {
            "id": "hot",
            "name": "熱門策略",
            "description": "優先選擇近期出現頻率較高的號碼"
        },
        {
            "id": "cold",
            "name": "冷門策略",
            "description": "優先選擇近期出現頻率較低的號碼"
        },
        {
            "id": "overdue",
            "name": "逾期策略",
            "description": "優先選擇超過平均間隔未出現的號碼"
        },
        {
            "id": "random",
            "name": "隨機策略",
            "description": "完全隨機選擇號碼"
        }
    ]
    
    return ResponseBase(
        success=True,
        message="獲取策略列表成功",
        data=strategies
    )
