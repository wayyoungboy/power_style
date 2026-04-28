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

    def promote(self, item: T, boost_multiplier: float = 1.0) -> T:
        """提升记忆强度。
        
        Args:
            item: 需要提升的记忆对象
            boost_multiplier: 提升倍率，如果需要一次性实现“多层跃迁”，可以传入更大的倍率 (如 3.0)。
        """
        item.strength = min(1.0, item.strength + (self.config.promotion_boost * boost_multiplier))
        item.last_accessed = datetime.now(timezone.utc)
        item.tier_level = self.calculate_tier(item.strength)
        return item

    def promote_to_tier(self, item: T, target_level: int) -> T:
        """直接指定多层跨越：将记忆直接提拔到某个特定的层级"""
        target_tier = next((t for t in self.sorted_tiers if t.level == target_level), None)
        if target_tier:
            # 直接将强度拉到目标层级的及格线（如果当前更强则保持不变）
            item.strength = max(item.strength, target_tier.threshold)
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

class LRUMemoryManager(MemoryManager):
    """LRU (Least Recently Used) 调度器
    一种硬性淘汰策略，如果在指定天数内未被访问，则记忆强度瞬间归零，直接打入冷宫。
    适合对上下文“时效性”要求极高、不需要平滑过渡的场景。
    """
    def demote(self, item: T) -> T:
        now = datetime.now(timezone.utc)
        days_passed = (now - item.last_accessed).days
        
        # 比如硬性阈值是 3 天，超过 3 天未访问直接清零
        threshold_days = getattr(self.config, 'lru_threshold_days', 3)
        
        if days_passed >= threshold_days:
            item.strength = 0.0
            item.tier_level = self.calculate_tier(item.strength)
            
        return item

class VolatileMemoryManager(MemoryManager):
    """易失性记忆调度器 (Volatile Memory)
    类似 RAM 的行为：除了刚刚被 promote 的数据，所有数据在下一次流转时都会被极速降级。
    """
    def demote(self, item: T) -> T:
        now = datetime.now(timezone.utc)
        days_passed = (now - item.last_accessed).days
        
        if days_passed > 0:
            # 每天暴跌 0.8 的强度，基本上一天不看就直接忘光
            item.strength = max(0.0, item.strength - 0.8)
            item.tier_level = self.calculate_tier(item.strength)
            
        return item

class FrequencyMemoryManager(MemoryManager):
    """LFU (Least Frequently Used) 调度器
    记忆的衰减速度与它的“历史访问总次数”成反比。
    被提及（访问）次数越多的记忆，它“变得更顽固”，抗衰减能力越强。
    """
    def demote(self, item: T) -> T:
        now = datetime.now(timezone.utc)
        days_passed = (now - item.last_accessed).days
        
        if days_passed > 0:
            # 假设 item 的 metadata 里记录了 access_count (访问频次)
            access_count = 1
            if hasattr(item, 'metadata') and item.metadata:
                access_count = item.metadata.get('access_count', 1)
            
            # 频次越高，衰减抵消系数越小（衰减越慢）
            # 比如访问了 10 次，衰减率就是原来的 1/10
            resistance = max(1, access_count)
            decay = (days_passed * self.config.decay_rate_per_day) / resistance
            
            item.strength = max(0.0, item.strength - decay)
            item.tier_level = self.calculate_tier(item.strength)
            
        return item

