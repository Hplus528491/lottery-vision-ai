"""
彩券模型

定義彩券資料表結構
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum, Index
from sqlalchemy.orm import relationship
import enum

from ..database import Base


class LotteryType(str, enum.Enum):
    """彩券類型枚舉"""
    BIG_LOTTERY = "big_lottery"      # 大樂透
    POWER_LOTTERY = "power_lottery"  # 威力彩
    DAILY_539 = "daily_539"          # 今彩539
    SUPER_LOTTO = "super_lotto"      # 雙贏彩
    LOTTO_649 = "lotto_649"          # 樂合彩


class LotteryDraw(Base):
    """彩券開獎記錄模型"""
    
    __tablename__ = "lottery_draws"
    
    # 主鍵
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 彩券信息
    lottery_type = Column(String(50), nullable=False, index=True)
    draw_number = Column(String(20), nullable=False)  # 期數
    draw_date = Column(DateTime, nullable=False, index=True)
    
    # 開獎號碼 (JSON 格式存儲)
    numbers = Column(JSON, nullable=False)  # 主要號碼
    special_number = Column(Integer, nullable=True)  # 特別號
    
    # 獎金信息 (JSON 格式存儲)
    prize_info = Column(JSON, nullable=True)
    
    # 統計信息
    total_sales = Column(Integer, nullable=True)  # 總銷售額
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 索引
    __table_args__ = (
        Index('ix_lottery_type_draw_date', 'lottery_type', 'draw_date'),
        Index('ix_lottery_type_draw_number', 'lottery_type', 'draw_number', unique=True),
    )
    
    def __repr__(self):
        return f"<LotteryDraw(id={self.id}, type={self.lottery_type}, draw={self.draw_number})>"


class LotteryStatistics(Base):
    """彩券統計模型"""
    
    __tablename__ = "lottery_statistics"
    
    # 主鍵
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 統計信息
    lottery_type = Column(String(50), nullable=False, index=True)
    number = Column(Integer, nullable=False)  # 號碼
    
    # 統計數據
    frequency = Column(Integer, default=0)  # 出現次數
    last_appeared = Column(DateTime, nullable=True)  # 最後出現日期
    average_interval = Column(Integer, nullable=True)  # 平均間隔期數
    max_interval = Column(Integer, nullable=True)  # 最大間隔期數
    current_interval = Column(Integer, default=0)  # 當前間隔期數
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 索引
    __table_args__ = (
        Index('ix_lottery_type_number', 'lottery_type', 'number', unique=True),
    )
    
    def __repr__(self):
        return f"<LotteryStatistics(type={self.lottery_type}, number={self.number}, freq={self.frequency})>"
