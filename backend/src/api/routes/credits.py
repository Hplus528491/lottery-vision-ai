"""
積分 API 路由

處理用戶積分查詢、交易記錄和套餐購買
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ...database import get_db
from ...models import User, CreditTransaction, CreditPackage
from ...exceptions import NotFoundError, ErrorCode
from ...utils import get_current_user
from ..schemas import (
    CreditBalanceResponse,
    CreditTransactionResponse,
    CreditTransactionListResponse,
    CreditPackageResponse,
    CreditPackageListResponse,
    ResponseBase
)


router = APIRouter(prefix="/credits", tags=["積分"])


@router.get("/balance", response_model=CreditBalanceResponse)
async def get_credit_balance(
    current_user: User = Depends(get_current_user)
):
    """
    獲取用戶積分餘額
    """
    return CreditBalanceResponse(
        success=True,
        message="獲取積分餘額成功",
        credits=current_user.credits,
        user_id=current_user.id
    )


@router.get("/transactions", response_model=CreditTransactionListResponse)
async def get_credit_transactions(
    transaction_type: Optional[str] = Query(None, description="交易類型"),
    page: int = Query(1, ge=1, description="頁碼"),
    page_size: int = Query(20, ge=1, le=100, description="每頁數量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    獲取用戶積分交易記錄
    """
    query = db.query(CreditTransaction).filter(
        CreditTransaction.user_id == current_user.id
    )
    
    if transaction_type:
        query = query.filter(CreditTransaction.transaction_type == transaction_type)
    
    # 計算總數
    total = query.count()
    
    # 分頁
    transactions = query.order_by(desc(CreditTransaction.created_at)) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()
    
    return CreditTransactionListResponse(
        success=True,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
        data=[CreditTransactionResponse.model_validate(t) for t in transactions]
    )


@router.get("/packages", response_model=CreditPackageListResponse)
async def get_credit_packages(
    db: Session = Depends(get_db)
):
    """
    獲取可購買的積分套餐
    """
    packages = db.query(CreditPackage) \
        .filter(CreditPackage.is_active == 1) \
        .order_by(CreditPackage.sort_order) \
        .all()
    
    return CreditPackageListResponse(
        success=True,
        message="獲取積分套餐成功",
        data=[CreditPackageResponse.model_validate(p) for p in packages]
    )


@router.post("/purchase/{package_id}", response_model=ResponseBase)
async def purchase_credits(
    package_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    購買積分套餐 (MVP 版本 - 虛擬購買)
    
    注意: 這是 MVP 版本，實際支付功能將在後續版本中實現
    """
    # 查找套餐
    package = db.query(CreditPackage) \
        .filter(
            CreditPackage.id == package_id,
            CreditPackage.is_active == 1
        ) \
        .first()
    
    if not package:
        raise NotFoundError(
            error_code=ErrorCode.PACKAGE_NOT_FOUND,
            message="積分套餐不存在"
        )
    
    # 計算總積分
    total_credits = package.credits + package.bonus_credits
    
    # 記錄交易前餘額
    balance_before = current_user.credits
    
    # 增加積分
    current_user.credits += total_credits
    
    # 記錄交易
    transaction = CreditTransaction(
        user_id=current_user.id,
        transaction_type="purchase",
        amount=total_credits,
        balance_before=balance_before,
        balance_after=current_user.credits,
        description=f"購買積分套餐: {package.name}",
        reference_id=package.id,
        reference_type="credit_package"
    )
    db.add(transaction)
    db.commit()
    
    return ResponseBase(
        success=True,
        message=f"購買成功！獲得 {total_credits} 積分",
        data={
            "credits_added": total_credits,
            "new_balance": current_user.credits
        }
    )


@router.get("/summary", response_model=ResponseBase)
async def get_credit_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    獲取用戶積分摘要
    
    包括總收入、總支出、當前餘額等
    """
    # 計算總收入
    total_income = db.query(CreditTransaction) \
        .filter(
            CreditTransaction.user_id == current_user.id,
            CreditTransaction.amount > 0
        ) \
        .with_entities(db.func.sum(CreditTransaction.amount)) \
        .scalar() or 0
    
    # 計算總支出
    total_expense = db.query(CreditTransaction) \
        .filter(
            CreditTransaction.user_id == current_user.id,
            CreditTransaction.amount < 0
        ) \
        .with_entities(db.func.sum(CreditTransaction.amount)) \
        .scalar() or 0
    
    # 計算推薦次數
    recommendation_count = db.query(CreditTransaction) \
        .filter(
            CreditTransaction.user_id == current_user.id,
            CreditTransaction.transaction_type == "recommendation"
        ) \
        .count()
    
    return ResponseBase(
        success=True,
        message="獲取積分摘要成功",
        data={
            "current_balance": current_user.credits,
            "total_income": total_income,
            "total_expense": abs(total_expense),
            "recommendation_count": recommendation_count
        }
    )
