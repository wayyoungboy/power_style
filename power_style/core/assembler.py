from abc import ABC, abstractmethod
from typing import List, Dict, Any, TypeVar
from power_style.core.models import MemoryItem
from power_style.core.config import FrameworkConfig, default_config

# 组装器同样支持任意继承自 MemoryItem 的子类
T = TypeVar('T', bound=MemoryItem)

class AssemblyAlgorithm(ABC):
    """算法插件的抽象基类"""
    @abstractmethod
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        pass

class ItemAssembler:
    """通用的动态策略引擎，基于注册的算法插件进行分派组装"""
    
    def __init__(self, config: FrameworkConfig = default_config):
        self.config = config
        self._algorithms: Dict[str, AssemblyAlgorithm] = {}
        
    def register_algorithm(self, name: str, algorithm: AssemblyAlgorithm):
        """注册一个算法插件"""
        self._algorithms[name] = algorithm

    def assemble(self, all_items: List[T], context: Dict[str, Any]) -> Dict[int, List[T]]:
        """主入口：按层级动态匹配对应算法插件，进行组装"""
        assembled_results: Dict[int, List[T]] = {}
        
        tiered_items: Dict[int, List[T]] = {t.level: [] for t in self.config.tiers}
        for item in all_items:
            if item.tier_level in tiered_items:
                tiered_items[item.tier_level].append(item)
                
        for tier in self.config.tiers:
            items_in_tier = tiered_items[tier.level]
            if not items_in_tier:
                assembled_results[tier.level] = []
                continue
                
            algo_name = tier.algorithm
            algo_plugin = self._algorithms.get(algo_name)
            
            if algo_plugin:
                assembled_results[tier.level] = algo_plugin.execute(items_in_tier, context, self.config)
            else:
                # 找不到算法插件，原样返回作为兜底
                assembled_results[tier.level] = items_in_tier

        return assembled_results

# 全局单例的组装器
global_assembler = ItemAssembler()
