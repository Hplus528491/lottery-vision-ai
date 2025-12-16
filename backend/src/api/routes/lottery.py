"""
彩券 API 路由

處理彩券數據查詢和統計分析
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from ...database import get_db
from ...models import LotteryDraw, LotteryStatistics, LotteryType
from ...exceptions import NotFoundError, ErrorCode
from ..schemas import (
    LotteryDrawResponse,
    LotteryDrawListResponse,
    LotteryStatisticsResponse,
    LotteryAnalysisResponse,
    NumberFrequencyResponse,
    ResponseBase
)


router = APIRouter(prefix="/lottery", tags=["彩券"])


@router.get("/types", response_model=ResponseBase)
async def get_lottery_types():
    """
    獲取所有彩券類型
    """
    types = [
        {"id": "big_lottery", "name": "大樂透", "numbers_count": 6, "max_number": 49, "has_special": True},
        {"id": "power_lottery", "name": "威力彩", "numbers_count": 6, "max_number": 38, "has_special": True},
        {"id": "daily_539", "name": "今彩539", "numbers_count": 5, "max_number": 39, "has_special": False},
        {"id": "super_lotto", "name": "雙贏彩", "numbers_count": 12, "max_number": 24, "has_special": False},
    ]
    
    return ResponseBase(
        success=True,
        message="獲取彩券類型成功",
        data=types
    )


@router.get("/draws", response_model=LotteryDrawListResponse)
async def get_lottery_draws(
    lottery_type: Optional[str] = Query(None, description="彩券類型"),
    page: int = Query(1, ge=1, description="頁碼"),
    page_size: int = Query(20, ge=1, le=100, description="每頁數量"),
    db: Session = Depends(get_db)
):
    """
    獲取彩券開獎記錄
    
    支持按彩券類型篩選和分頁
    """
    query = db.query(LotteryDraw)
    
    if lottery_type:
        query = query.filter(LotteryDraw.lottery_type == lottery_type)
    
    # 計算總數
    total = query.count()
    
    # 分頁
    draws = query.order_by(desc(LotteryDraw.draw_date)) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()
    
    return LotteryDrawListResponse(
        success=True,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
        data=[LotteryDrawResponse.model_validate(d) for d in draws]
    )


@router.get("/draws/{draw_id}", response_model=LotteryDrawResponse)
async def get_lottery_draw(
    draw_id: int,
    db: Session = Depends(get_db)
):
    """
    獲取單個開獎記錄
    """
    draw = db.query(LotteryDraw).filter(LotteryDraw.id == draw_id).first()
    
    if not draw:
        raise NotFoundError(
            error_code=ErrorCode.DRAW_NOT_FOUND,
            message="開獎記錄不存在"
        )
    
    return LotteryDrawResponse.model_validate(draw)


@router.get("/latest/{lottery_type}", response_model=LotteryDrawResponse)
async def get_latest_draw(
    lottery_type: str,
    db: Session = Depends(get_db)
):
    """
    獲取最新開獎記錄
    """
    draw = db.query(LotteryDraw) \
        .filter(LotteryDraw.lottery_type == lottery_type) \
        .order_by(desc(LotteryDraw.draw_date)) \
        .first()
    
    if not draw:
        raise NotFoundError(
            error_code=ErrorCode.DRAW_NOT_FOUND,
            message="尚無開獎記錄"
        )
    
    return LotteryDrawResponse.model_validate(draw)


@router.get("/statistics/{lottery_type}", response_model=ResponseBase)
async def get_lottery_statistics(
    lottery_type: str,
    db: Session = Depends(get_db)
):
    """
    獲取彩券統計數據
    
    包括號碼出現頻率、熱門號碼、冷門號碼等
    """
    stats = db.query(LotteryStatistics) \
        .filter(LotteryStatistics.lottery_type == lottery_type) \
        .order_by(desc(LotteryStatistics.frequency)) \
        .all()
    
    if not stats:
        return ResponseBase(
            success=True,
            message="尚無統計數據",
            data=[]
        )
    
    return ResponseBase(
        success=True,
        message="獲取統計數據成功",
        data=[LotteryStatisticsResponse.model_validate(s) for s in stats]
    )


@router.get("/analysis/{lottery_type}", response_model=LotteryAnalysisResponse)
async def get_lottery_analysis(
    lottery_type: str,
    db: Session = Depends(get_db)
):
    """
    獲取彩券分析報告
    
    包括熱門號碼、冷門號碼、逾期號碼等分析
    """
    # 獲取總開獎次數
    total_draws = db.query(LotteryDraw) \
        .filter(LotteryDraw.lottery_type == lottery_type) \
        .count()
    
    # 獲取統計數據
    stats = db.query(LotteryStatistics) \
        .filter(LotteryStatistics.lottery_type == lottery_type) \
        .all()
    
    if not stats:
        return LotteryAnalysisResponse(
            success=True,
            lottery_type=lottery_type,
            total_draws=total_draws,
            hot_numbers=[],
            cold_numbers=[],
            overdue_numbers=[],
            recent_numbers=[]
        )
    
    # 計算熱門號碼 (出現頻率最高的 10 個)
    sorted_by_freq = sorted(stats, key=lambda x: x.frequency, reverse=True)
    hot_numbers = [
        NumberFrequencyResponse(
            number=s.number,
            frequency=s.frequency,
            percentage=round(s.frequency / total_draws * 100, 2) if total_draws > 0 else 0
        )
        for s in sorted_by_freq[:10]
    ]
    
    # 計算冷門號碼 (出現頻率最低的 10 個)
    cold_numbers = [
        NumberFrequencyResponse(
            number=s.number,
            frequency=s.frequency,
            percentage=round(s.frequency / total_draws * 100, 2) if total_draws > 0 else 0
        )
        for s in sorted_by_freq[-10:]
    ]
    
    # 計算逾期號碼 (當前間隔超過平均間隔的號碼)
    overdue_numbers = [
        s.number for s in stats
        if s.average_interval and s.current_interval > s.average_interval
    ]
    
    # 獲取最近開獎號碼
    recent_draws = db.query(LotteryDraw) \
        .filter(LotteryDraw.lottery_type == lottery_type) \
        .order_by(desc(LotteryDraw.draw_date)) \
        .limit(5) \
        .all()
    
    recent_numbers = [d.numbers for d in recent_draws]
    
    return LotteryAnalysisResponse(
        success=True,
        lottery_type=lottery_type,
        total_draws=total_draws,
        hot_numbers=hot_numbers,
        cold_numbers=cold_numbers,
        overdue_numbers=overdue_numbers,
        recent_numbers=recent_numbers
    )
