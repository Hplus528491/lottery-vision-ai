"""
推薦模型

定義 AI 推薦資料表結構
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text, Float
from sqlalchemy.orm import relationship

from ..database import Base


class Recommendation(Base):
    """AI 推薦記錄模型"""
    
    __tablename__ = "recommendations"
    
    # 主鍵
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 用戶關聯
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 推薦信息
    lottery_type = Column(String(50), nullable=False, index=True)
    recommended_numbers = Column(JSON, nullable=False)  # 推薦號碼
    special_number = Column(Integer, nullable=True)  # 推薦特別號
    
    # AI 分析
    analysis = Column(Text, nullable=True)  # AI 分析說明
    confidence_score = Column(Float, nullable=True)  # 信心分數 (0-1)
    strategy = Column(String(100), nullable=True)  # 推薦策略
    
    # 統計依據 (JSON 格式)
    statistics_basis = Column(JSON, nullable=True)
    
    # 積分消耗
    credits_used = Column(Integer, default=10)
    
    # 結果追蹤
    is_matched = Column(Integer, nullable=True)  # 中獎號碼數量
    prize_amount = Column(Integer, nullable=True)  # 中獎金額
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    user = relationship("User", back_populates="recommendations")
    
    def __repr__(self):
        return f"<Recommendation(id={self.id}, user_id={self.user_id}, type={self.lottery_type})>"


class RecommendationStrategy(Base):
    """推薦策略模型"""
    
    __tablename__ = "recommendation_strategies"
    
    # 主鍵
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 策略信息
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # 策略參數 (JSON 格式)
    parameters = Column(JSON, nullable=True)
    
    # 狀態
    is_active = Column(Integer, default=1)
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<RecommendationStrategy(id={self.id}, name={self.name})>"
