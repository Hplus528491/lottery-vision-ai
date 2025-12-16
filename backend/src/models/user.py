"""
用戶模型

定義用戶資料表結構
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship

from ..database import Base


class User(Base):
    """用戶模型"""
    
    __tablename__ = "users"
    
    # 主鍵
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 基本信息
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # 個人資料
    full_name = Column(String(200), nullable=True)
    avatar_url = Column(Text, nullable=True)
    
    # 狀態
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # 虛擬積分
    credits = Column(Integer, default=100)
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    # 關聯
    recommendations = relationship("Recommendation", back_populates="user")
    credit_transactions = relationship("CreditTransaction", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
