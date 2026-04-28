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

# --- 扩展算法库 (Expanded Standard Library) ---

class StrengthSortAlgorithm(AssemblyAlgorithm):
    """算法6：纯按记忆强度降序排列"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        limit = context.get("limit", len(items))
        return sorted(items, key=lambda x: x.strength, reverse=True)[:limit]

class RecencySortAlgorithm(AssemblyAlgorithm):
    """算法7：纯按最近访问时间降序排列 (最新鲜的在前)"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        limit = context.get("limit", len(items))
        return sorted(items, key=lambda x: x.last_accessed, reverse=True)[:limit]

class RandomSampleAlgorithm(AssemblyAlgorithm):
    """算法8：随机采样 (常用于增加 LLM 记忆的多样性与创造性)"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        import random
        limit = context.get("limit", len(items))
        if not items: return []
        sample_size = min(limit, len(items))
        return random.sample(items, sample_size)

class DeduplicationAlgorithm(AssemblyAlgorithm):
    """算法9：内容去重算法"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        seen = set()
        unique_items = []
        for item in items:
            if item.content not in seen:
                seen.add(item.content)
                unique_items.append(item)
        return unique_items

class MetadataFilterAlgorithm(AssemblyAlgorithm):
    """算法10：基于元数据键值对的精确过滤"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        meta_key = context.get("meta_key")
        meta_val = context.get("meta_val")
        if not meta_key: return items
        return [i for i in items if i.metadata and i.metadata.get(meta_key) == meta_val]

class MetadataSortAlgorithm(AssemblyAlgorithm):
    """算法11：基于元数据数值型字段进行排序"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        meta_key = context.get("meta_key")
        reverse = context.get("reverse", True)
        if not meta_key: return items
        return sorted(items, key=lambda x: float(x.metadata.get(meta_key, 0) if x.metadata else 0), reverse=reverse)

class LengthTruncateAlgorithm(AssemblyAlgorithm):
    """算法12：硬性长度截断 (防止打爆 LLM Context Window)"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        max_length = context.get("max_length", 8000)
        current_length = 0
        truncated = []
        for item in items:
            item_len = len(item.content)
            if current_length + item_len <= max_length:
                truncated.append(item)
                current_length += item_len
            else:
                break
        return truncated

class LengthSortAlgorithm(AssemblyAlgorithm):
    """算法13：按内容长度排序 (可用于优先展示短规则)"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        reverse = context.get("reverse", False)
        return sorted(items, key=lambda x: len(x.content), reverse=reverse)

class TierFilterAlgorithm(AssemblyAlgorithm):
    """算法14：仅提取指定 Tier 层级的数据"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        target_tier = context.get("target_tier", 1)
        return [i for i in items if i.tier_level == target_tier]

class TitleMatchAlgorithm(AssemblyAlgorithm):
    """算法15：精确匹配标题"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        target_title = context.get("target_title", "")
        return [i for i in items if getattr(i, 'title', '') == target_title]

class RegexMatchAlgorithm(AssemblyAlgorithm):
    """算法16：基于正则表达式的内容匹配"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        import re
        pattern_str = context.get("regex_pattern", "")
        if not pattern_str: return items
        pattern = re.compile(pattern_str)
        return [i for i in items if pattern.search(i.content)]

class CategoryGroupAlgorithm(AssemblyAlgorithm):
    """算法17：分组后每个类别只取 Top 1"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        seen_categories = set()
        results = []
        for item in sorted(items, key=lambda x: x.strength, reverse=True):
            cat = getattr(item, 'category', 'default')
            if cat not in seen_categories:
                seen_categories.add(cat)
                results.append(item)
        return results

class ScoreThresholdAlgorithm(AssemblyAlgorithm):
    """算法18：一刀切：只保留强度大于某阈值的记忆"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        min_strength = context.get("min_strength", 0.5)
        return [i for i in items if i.strength >= min_strength]

class FirstNAlgorithm(AssemblyAlgorithm):
    """算法19：Head Slice (直接取前N个)"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        n = context.get("n", 5)
        return items[:n]

class LastNAlgorithm(AssemblyAlgorithm):
    """算法20：Tail Slice (直接取后N个)"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        n = context.get("n", 5)
        return items[-n:] if n > 0 else []

class ShuffleAlgorithm(AssemblyAlgorithm):
    """算法21：完全打乱顺序 (打乱 LLM 偏好位置权重)"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        import random
        copied = list(items)
        random.shuffle(copied)
        return copied

class JaccardSimilarityAlgorithm(AssemblyAlgorithm):
    """算法22：杰卡德字符级相似度匹配 (轻量级本地化匹配)"""
    def execute(self, items: List[T], context: Dict[str, Any], config: FrameworkConfig) -> List[T]:
        query = context.get("query", "")
        if not query: return items
        
        query_set = set(query.lower().split())
        if not query_set: return items
        
        def jaccard_score(item: T) -> float:
            item_set = set(item.content.lower().split())
            if not item_set: return 0.0
            intersection = query_set.intersection(item_set)
            union = query_set.union(item_set)
            return len(intersection) / len(union)
            
        sorted_items = sorted(items, key=jaccard_score, reverse=True)
        return sorted_items[:context.get("limit", 5)]

