from typing import List, TypeVar
from datetime import datetime, timezone
from power_style.core.models import MemoryItem
from power_style.core.config import FrameworkConfig, default_config

# 使用泛型，支持所有继承自 MemoryItem 的特化子类
T = TypeVar('T', bound=MemoryItem)

class MemoryManager:
    """通用的记忆调度器：处理层数不限的动态升降级"""
    
    def __init__(self, config: FrameworkConfig = default_config):
        self.config = config
        self.sorted_tiers = sorted(self.config.tiers, key=lambda t: t.level)

    def calculate_tier(self, strength: float) -> int:
        for tier in self.sorted_tiers:
            if strength >= tier.threshold:
                return tier.level
        return self.sorted_tiers[-1].level

    def promote(self, item: T) -> T:
        item.strength = min(1.0, item.strength + self.config.promotion_boost)
        item.last_accessed = datetime.now(timezone.utc)
        item.tier_level = self.calculate_tier(item.strength)
        return item

    def demote(self, item: T) -> T:
        now = datetime.now(timezone.utc)
        days_passed = (now - item.last_accessed).days
        if days_passed > 0:
            decay = days_passed * self.config.decay_rate_per_day
            item.strength = max(0.0, item.strength - decay)
            item.tier_level = self.calculate_tier(item.strength)
        return item

    def process_items(self, items: List[T]) -> List[T]:
        """批量处理衰减与分层"""
        return [self.demote(item) for item in items]

class EbbinghausMemoryManager(MemoryManager):
    """艾宾浩斯遗忘曲线调度器
    使用指数衰减模型模拟人类大脑的遗忘机制，而非线性衰减。
    公式: R = e^(-t/S) (简化版)
    """
    def demote(self, item: T) -> T:
        import math
        now = datetime.now(timezone.utc)
        days_passed = (now - item.last_accessed).days
        
        if days_passed > 0:
            # 引入半衰期概念（比如7天）
            # days_passed 越大，遗忘越快；但基础 strength 如果很高，则下降平缓
            decay_factor = math.exp(-days_passed / 7.0)
            
            # 使用遗忘因子重新计算当前记忆强度
            item.strength = item.strength * decay_factor
            item.tier_level = self.calculate_tier(item.strength)
            
        return item
