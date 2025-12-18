"""
AI 推薦器模組

使用 Claude AI 進行智慧號碼推薦
"""

import random
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..config import settings
from ..models import LotteryStatistics, LotteryDraw


# 彩券配置
LOTTERY_CONFIG = {
    "big_lottery": {
        "name": "大樂透",
        "numbers_count": 6,
        "max_number": 49,
        "has_special": True,
        "special_max": 49
    },
    "power_lottery": {
        "name": "威力彩",
        "numbers_count": 6,
        "max_number": 38,
        "has_special": True,
        "special_max": 8
    },
    "daily_539": {
        "name": "今彩539",
        "numbers_count": 5,
        "max_number": 39,
        "has_special": False
    },
    "super_lotto": {
        "name": "雙贏彩",
        "numbers_count": 12,
        "max_number": 24,
        "has_special": False
    }
}


class AIRecommender:
    """AI 推薦器類"""
    
    def __init__(self, db: Session):
        """
        初始化推薦器
        
        Args:
            db: 資料庫會話
        """
        self.db = db
        self.client = None
        
        if OPENAI_AVAILABLE and settings.MANUS_API_KEY:
            self.client = OpenAI(
                api_key=settings.MANUS_API_KEY,
                base_url=settings.MANUS_API_BASE_URL
            )
    
    async def generate_recommendation(
        self,
        lottery_type: str,
        strategy: str = "balanced",
        statistics: List[LotteryStatistics] = None
    ) -> Dict[str, Any]:
        """
        生成推薦號碼
        
        Args:
            lottery_type: 彩券類型
            strategy: 推薦策略
            statistics: 統計數據
            
        Returns:
            Dict: 推薦結果
        """
        config = LOTTERY_CONFIG.get(lottery_type)
        if not config:
            raise ValueError(f"不支持的彩券類型: {lottery_type}")
        
        # 根據策略生成號碼
        if strategy == "random":
            numbers = self._generate_random(config)
        elif strategy == "hot":
            numbers = self._generate_hot(config, statistics)
        elif strategy == "cold":
            numbers = self._generate_cold(config, statistics)
        elif strategy == "overdue":
            numbers = self._generate_overdue(config, statistics)
        else:  # balanced
            numbers = self._generate_balanced(config, statistics)
        
        # 生成特別號
        special_number = None
        if config.get("has_special"):
            special_number = random.randint(1, config.get("special_max", config["max_number"]))
        
        # 嘗試使用 AI 生成分析
        analysis = await self._generate_ai_analysis(
            lottery_type=lottery_type,
            numbers=numbers,
            special_number=special_number,
            strategy=strategy,
            statistics=statistics
        )
        
        # 計算信心分數
        confidence_score = self._calculate_confidence(numbers, statistics)
        
        return {
            "numbers": sorted(numbers),
            "special_number": special_number,
            "analysis": analysis,
            "confidence_score": confidence_score,
            "statistics_basis": self._get_statistics_basis(numbers, statistics)
        }
    
    def _generate_random(self, config: Dict) -> List[int]:
        """隨機生成號碼"""
        return random.sample(range(1, config["max_number"] + 1), config["numbers_count"])
    
    def _generate_hot(self, config: Dict, statistics: List[LotteryStatistics]) -> List[int]:
        """基於熱門號碼生成"""
        if not statistics:
            return self._generate_random(config)
        
        # 按頻率排序
        sorted_stats = sorted(statistics, key=lambda x: x.frequency, reverse=True)
        hot_numbers = [s.number for s in sorted_stats[:config["numbers_count"] * 2]]
        
        # 從熱門號碼中隨機選擇
        if len(hot_numbers) >= config["numbers_count"]:
            return random.sample(hot_numbers, config["numbers_count"])
        else:
            return self._generate_random(config)
    
    def _generate_cold(self, config: Dict, statistics: List[LotteryStatistics]) -> List[int]:
        """基於冷門號碼生成"""
        if not statistics:
            return self._generate_random(config)
        
        # 按頻率排序 (升序)
        sorted_stats = sorted(statistics, key=lambda x: x.frequency)
        cold_numbers = [s.number for s in sorted_stats[:config["numbers_count"] * 2]]
        
        # 從冷門號碼中隨機選擇
        if len(cold_numbers) >= config["numbers_count"]:
            return random.sample(cold_numbers, config["numbers_count"])
        else:
            return self._generate_random(config)
    
    def _generate_overdue(self, config: Dict, statistics: List[LotteryStatistics]) -> List[int]:
        """基於逾期號碼生成"""
        if not statistics:
            return self._generate_random(config)
        
        # 找出逾期號碼
        overdue_numbers = [
            s.number for s in statistics
            if s.average_interval and s.current_interval > s.average_interval
        ]
        
        if len(overdue_numbers) >= config["numbers_count"]:
            return random.sample(overdue_numbers, config["numbers_count"])
        else:
            # 補充隨機號碼
            remaining = config["numbers_count"] - len(overdue_numbers)
            all_numbers = set(range(1, config["max_number"] + 1))
            available = list(all_numbers - set(overdue_numbers))
            return overdue_numbers + random.sample(available, remaining)
    
    def _generate_balanced(self, config: Dict, statistics: List[LotteryStatistics]) -> List[int]:
        """平衡策略生成"""
        if not statistics:
            return self._generate_random(config)
        
        numbers_count = config["numbers_count"]
        
        # 熱門號碼 (40%)
        hot_count = max(1, numbers_count * 2 // 5)
        sorted_by_freq = sorted(statistics, key=lambda x: x.frequency, reverse=True)
        hot_numbers = [s.number for s in sorted_by_freq[:hot_count * 2]]
        selected_hot = random.sample(hot_numbers, min(hot_count, len(hot_numbers)))
        
        # 冷門號碼 (30%)
        cold_count = max(1, numbers_count * 3 // 10)
        cold_numbers = [s.number for s in sorted_by_freq[-cold_count * 2:]]
        available_cold = [n for n in cold_numbers if n not in selected_hot]
        selected_cold = random.sample(available_cold, min(cold_count, len(available_cold)))
        
        # 隨機號碼 (30%)
        random_count = numbers_count - len(selected_hot) - len(selected_cold)
        all_numbers = set(range(1, config["max_number"] + 1))
        used_numbers = set(selected_hot + selected_cold)
        available = list(all_numbers - used_numbers)
        selected_random = random.sample(available, random_count)
        
        return selected_hot + selected_cold + selected_random
    
    async def _generate_ai_analysis(
        self,
        lottery_type: str,
        numbers: List[int],
        special_number: Optional[int],
        strategy: str,
        statistics: List[LotteryStatistics]
    ) -> str:
        """使用 AI 生成分析說明"""
        
        if not self.client:
            return self._generate_default_analysis(lottery_type, numbers, strategy)
        
        try:
            config = LOTTERY_CONFIG[lottery_type]
            
            # 準備統計摘要
            stats_summary = ""
            if statistics:
                sorted_stats = sorted(statistics, key=lambda x: x.frequency, reverse=True)
                hot_nums = [s.number for s in sorted_stats[:5]]
                cold_nums = [s.number for s in sorted_stats[-5:]]
                stats_summary = f"熱門號碼: {hot_nums}, 冷門號碼: {cold_nums}"
            
            prompt = f"""
            你是一位彩券分析專家。請為以下推薦號碼提供簡短的分析說明（50-100字）：
            
            彩券類型: {config['name']}
            推薦號碼: {sorted(numbers)}
            特別號: {special_number if special_number else '無'}
            使用策略: {strategy}
            統計摘要: {stats_summary}
            
            請用繁體中文回覆，說明這組號碼的選擇依據和特點。
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return self._generate_default_analysis(lottery_type, numbers, strategy)
    
    def _generate_default_analysis(
        self,
        lottery_type: str,
        numbers: List[int],
        strategy: str
    ) -> str:
        """生成默認分析說明"""
        config = LOTTERY_CONFIG[lottery_type]
        strategy_names = {
            "balanced": "平衡策略",
            "hot": "熱門策略",
            "cold": "冷門策略",
            "overdue": "逾期策略",
            "random": "隨機策略"
        }
        
        return f"本次推薦採用{strategy_names.get(strategy, '平衡策略')}，" \
               f"從 {config['name']} 的歷史數據中分析選出 {len(numbers)} 個號碼。" \
               f"建議理性投注，祝您好運！"
    
    def _calculate_confidence(
        self,
        numbers: List[int],
        statistics: List[LotteryStatistics]
    ) -> float:
        """計算信心分數"""
        if not statistics:
            return 0.5
        
        # 基於統計數據計算信心分數
        stats_dict = {s.number: s for s in statistics}
        
        total_score = 0
        for num in numbers:
            if num in stats_dict:
                stat = stats_dict[num]
                # 考慮頻率和間隔
                freq_score = min(stat.frequency / 100, 1.0) * 0.5
                interval_score = 0.5 if stat.current_interval and stat.average_interval and \
                    stat.current_interval > stat.average_interval else 0.3
                total_score += freq_score + interval_score
        
        return round(total_score / len(numbers), 2)
    
    def _get_statistics_basis(
        self,
        numbers: List[int],
        statistics: List[LotteryStatistics]
    ) -> Dict[str, Any]:
        """獲取統計依據"""
        if not statistics:
            return {}
        
        stats_dict = {s.number: s for s in statistics}
        
        basis = {}
        for num in numbers:
            if num in stats_dict:
                stat = stats_dict[num]
                basis[str(num)] = {
                    "frequency": stat.frequency,
                    "current_interval": stat.current_interval,
                    "average_interval": stat.average_interval
                }
        
        return basis
