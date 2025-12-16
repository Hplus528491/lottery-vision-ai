"""
積分模型

定義虛擬積分資料表結構
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum

from ..database import Base


class TransactionType(str, enum.Enum):
    """交易類型枚舉"""
    INITIAL = "initial"          # 初始贈送
    PURCHASE = "purchase"        # 購買
    RECOMMENDATION = "recommendation"  # 推薦消耗
    REFUND = "refund"            # 退款
    BONUS = "bonus"              # 獎勵
    ADMIN = "admin"              # 管理員調整


class CreditTransaction(Base):
    """積分交易記錄模型"""
    
    __tablename__ = "credit_transactions"
    
    # 主鍵
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 用戶關聯
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 交易信息
    transaction_type = Column(String(50), nullable=False)
    amount = Column(Integer, nullable=False)  # 正數為增加，負數為減少
    balance_before = Column(Integer, nullable=False)  # 交易前餘額
    balance_after = Column(Integer, nullable=False)  # 交易後餘額
    
    # 描述
    description = Column(Text, nullable=True)
    
    # 關聯 ID (如推薦 ID、訂單 ID 等)
    reference_id = Column(Integer, nullable=True)
    reference_type = Column(String(50), nullable=True)
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    user = relationship("User", back_populates="credit_transactions")
    
    def __repr__(self):
        return f"<CreditTransaction(id={self.id}, user_id={self.user_id}, amount={self.amount})>"


class CreditPackage(Base):
    """積分套餐模型"""
    
    __tablename__ = "credit_packages"
    
    # 主鍵
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 套餐信息
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # 積分和價格
    credits = Column(Integer, nullable=False)  # 積分數量
    price = Column(Integer, nullable=False)  # 價格 (新台幣)
    bonus_credits = Column(Integer, default=0)  # 贈送積分
    
    # 狀態
    is_active = Column(Integer, default=1)
    sort_order = Column(Integer, default=0)
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CreditPackage(id={self.id}, name={self.name}, credits={self.credits})>"
