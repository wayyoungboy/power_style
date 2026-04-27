from typing import List, Dict, Any, TypeVar
from power_style.core.models import MemoryItem
from power_style.core.config import FrameworkConfig
from power_style.core.resources import resource_manager
from power_style.core.assembler import AssemblyAlgorithm

T = TypeVar('T', bound=MemoryItem)

class ExactMatchAlgorithm(AssemblyAlgorithm):
    """算法1：基础精确匹配过滤"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        filter_func = context.get("filter_func")
        if filter_func:
            return [i for i in items if filter_func(i)]
        return items

class VectorSearchAlgorithm(AssemblyAlgorithm):
    """算法2：向量检索"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        query = context.get("query", "")
        vector_db = resource_manager.get_vector()

        if not vector_db or not query:
            # 优雅降级回精确匹配
            fallback = ExactMatchAlgorithm()
            return fallback.execute(items, context, config)[:config.vector.top_k_default]
            
        search_results = vector_db.search(query, top_k=config.vector.top_k_default)
        matched_ids = {res["id"] for res in search_results}
        
        return [i for i in items if str(i.id) in matched_ids]

class LLMSummaryAlgorithm(AssemblyAlgorithm):
    """算法3：大模型归纳压缩"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        if not items:
            return []
            
        llm = resource_manager.get_llm()
        if not llm:
            # 优雅降级
            basic_content = "\n".join([f"- {i.content[:20]}" for i in items])
            fallback_item = MemoryItem(
                id="summary_fallback",
                content=f"LLM Resource not available. Raw data:\n{basic_content}",
                strength=0.1,
                tier_level=config.tiers[-1].level,
                metadata={"type": "summary"}
            )
            return [fallback_item]  # type: ignore

        items_text = "\n".join([f"- {i.content[:50]}" for i in items])
        prompt = config.prompts.summarize_prompt.format(rules_text=items_text)
        
        summary_content = llm.generate(prompt, context={"system_prompt": "You are compressing obsolete memory."})
        
        summary_item = MemoryItem(
            id="summary_archived",
            content=summary_content,
            strength=0.1,
            tier_level=config.tiers[-1].level,
            metadata={"type": "summary"}
        )
        return [summary_item]  # type: ignore

class KeywordMatchAlgorithm(AssemblyAlgorithm):
    """算法4：基础关键字匹配（常用于缺乏 Vector 时的降级，或精准搜索变量名）"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        query = context.get("query", "").lower()
        if not query:
            return items
            
        # 简单的关键字包含匹配
        matched_items = []
        for item in items:
            if query in item.content.lower() or query in getattr(item, 'title', '').lower():
                matched_items.append(item)
                
        return matched_items[:config.vector.top_k_default]

class TimeWeightSortAlgorithm(AssemblyAlgorithm):
    """算法5：时间与强度混合排序截断（常用于近期对话上下文保留）"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        if not items:
            return []
            
        limit = context.get("limit", 5)
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        def calculate_score(item: T) -> float:
            # 简单的打分：强度占70%，时间新鲜度占30%
            days_old = (now - item.last_accessed).days
            time_score = max(0.0, 1.0 - (days_old * 0.1))
            return (item.strength * 0.7) + (time_score * 0.3)
            
        # 按综合分数排序并截断
        sorted_items = sorted(items, key=calculate_score, reverse=True)
        return sorted_items[:limit]
