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
