import sys
import os
from datetime import datetime, timezone, timedelta

# Add parent to path for running from examples dir
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from power_style.core.models import MemoryItem
from power_style.core.memory_manager import EbbinghausMemoryManager
from power_style.core.config import default_config

def run_ebbinghaus_demo():
    print("=== 🧠 艾宾浩斯遗忘曲线模拟演示 ===")
    
    manager = EbbinghausMemoryManager(default_config)
    now = datetime.now(timezone.utc)
    
    # 创建几个不同时间点学习的记忆碎片
    items = [
        MemoryItem(
            id="item_just_now",
            content="刚刚学的单词：Apple",
            strength=1.0,
            last_accessed=now - timedelta(days=0)
        ),
        MemoryItem(
            id="item_1_day_ago",
            content="昨天学的单词：Banana",
            strength=1.0,
            last_accessed=now - timedelta(days=1)
        ),
        MemoryItem(
            id="item_7_days_ago",
            content="一周前学的单词：Cherry",
            strength=1.0,
            last_accessed=now - timedelta(days=7)
        ),
        MemoryItem(
            id="item_30_days_ago",
            content="一个月前学的单词：Durian",
            strength=1.0,
            last_accessed=now - timedelta(days=30)
        ),
    ]
    
    print("\n[初始状态] 所有记忆强度均为 1.0 (满级)\n")
    
    # 模拟时间流逝带来的衰减
    processed_items = manager.process_items(items)
    
    for item in processed_items:
        days = (now - item.last_accessed).days
        print(f"[{item.id}] (距今 {days:2d} 天)")
        print(f"  - 内容: {item.content}")
        print(f"  - 当前强度: {item.strength:.3f}")
        print(f"  - 当前所属层级: Tier {item.tier_level}")
        print("-" * 40)
        
    print("\n💡 结论：遗忘是指数级的！一周前的记忆衰退到 36%，而一个月前的记忆已经归零，掉入了最底层的 Tier 3。")
    print("如果此时调用 manager.promote(item)，则强度又会激增，这就模拟了'复习'的效果。")

if __name__ == "__main__":
    run_ebbinghaus_demo()
