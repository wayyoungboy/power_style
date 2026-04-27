import os
from power_style.core.config import default_config
from power_style.core.models import CodeStyleItem, ChatHistoryItem
from power_style.core.resources import resource_manager
from power_style.core.memory_manager import MemoryManager
from power_style.core.assembler import ItemAssembler
from power_style.plugins.llm_local_mock import LocalMockLLMResource
from power_style.plugins.algorithms import ExactMatchAlgorithm, VectorSearchAlgorithm, LLMSummaryAlgorithm

def run_framework_demo():
    print("=== 演示: 高度泛化的特化系统 (处理完全不同形态的数据) ===")
    local_llm = LocalMockLLMResource()
    resource_manager.register_llm("local_mock", local_llm, set_default=True)
    
    manager = MemoryManager(default_config)
    assembler = ItemAssembler(default_config)
    assembler.register_algorithm("exact_match", ExactMatchAlgorithm())
    assembler.register_algorithm("vector_search", VectorSearchAlgorithm())
    assembler.register_algorithm("llm_summary", LLMSummaryAlgorithm())
    
    print("\n--- 场景 A：作为【代码规则】使用 ---")
    rules = [
        CodeStyleItem(id="r1", title="FastAPI Guideline", content="Use async def.", category="python", strength=0.9),
        CodeStyleItem(id="r2", title="Old Pattern", content="Use threading.", category="python", strength=0.1),
    ]
    rules = manager.process_items(rules)
    
    # 我们可以通过自定义过滤函数让 exact_match 具备特化能力
    context_a = {
        "query": "async", 
        "filter_func": lambda item: getattr(item, "category", "") == "python"
    }
    
    rule_results = assembler.assemble(rules, context_a)
    for tier, result_items in rule_results.items():
        print(f"Tier {tier}:")
        for rr in result_items:
            # 即使被压缩成了基类 MemoryItem（比如在 L3），也能统一访问 content
            title = getattr(rr, "title", "Generic Item")
            print(f"  -> [{title}] {rr.content[:40]}...")

    print("\n--- 场景 B：作为【对话记忆】使用 ---")
    chats = [
        ChatHistoryItem(id="c1", session_id="sess_01", role="user", content="Hi, tell me a joke", strength=0.85),
        ChatHistoryItem(id="c2", session_id="sess_01", role="assistant", content="Why did the chicken...", strength=0.0),
    ]
    chats = manager.process_items(chats)
    
    context_b = {"query": "joke"}
    chat_results = assembler.assemble(chats, context_b)
    for tier, result_items in chat_results.items():
        print(f"Tier {tier}:")
        for cc in result_items:
            role = getattr(cc, "role", "system")
            print(f"  -> [{role}] {cc.content[:40]}...")

if __name__ == "__main__":
    run_framework_demo()
