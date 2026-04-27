<div align="center">
  <img src="docs/assets/hero.png" width="100%" alt="PowerStyle Hero Image">
  <h1>PowerStyle</h1>
  <p><strong>A Generic Multi-Tier Memory and Rule Scheduling Framework</strong></p>
</div>

---

## ⚡️ Overview

**PowerStyle** is an advanced, un-opinionated routing and dynamic assembly framework based on **Item Strength**. Originally inspired by the memory tiering mechanics of intelligent agents, it provides a decoupled architecture to manage any stateful items (Coding Rules, Chat History, Notifications, Agent Tools) by gracefully routing them across multiple processing algorithms.

### 🌟 Core Philosophy

Not all memory is created equal. **PowerStyle** allows you to configure dynamic strength thresholds (Tiers) for your data. As an item's strength decays over time or increases through usage, it smoothly shifts between different `AssemblyAlgorithm` plugins:

1.  **Tier 1 (High Strength)**: Immediate, exact match. 100% precision.
2.  **Tier 2 (Medium Strength)**: Vector-based semantic search. Relevant recall.
3.  **Tier 3 (Low Strength)**: LLM summarization. Highly compressed context.

## 🚀 Features

- **Multi-Tier Degradation:** Automatically handles the decay of unused memory and the promotion of actively used memory.
- **Resource Decoupling:** Pluggable `VectorResource` and `LLMResource` abstractions.
- **Algorithm Plugins:** Define custom behaviors via `AssemblyAlgorithm` (e.g., `ExactMatchAlgorithm`, `VectorSearchAlgorithm`, `LLMSummaryAlgorithm`).
- **Zero Business Logic:** PowerStyle knows nothing about your business models. Simply inherit from `MemoryItem` and let the `MemoryManager` and `ItemAssembler` do the heavy lifting.

## 🛠️ Quick Start

```python
from power_style.core.config import default_config
from power_style.core.memory_manager import MemoryManager
from power_style.core.assembler import global_assembler
from power_style.core.models import MemoryItem

# 1. Define your custom item
class ToolItem(MemoryItem):
    name: str
    schema: dict

# 2. Process and decay items
manager = MemoryManager(default_config)
items = manager.process_items(my_tools_list)

# 3. Assemble context dynamically based on tier
context = {"query": "parse JSON"}
assembled_tiers = global_assembler.assemble(items, context)

print(assembled_tiers[1]) # Exact tools
print(assembled_tiers[2]) # Semantically matched tools
```

## 🏗️ Architecture

- **`core.models.MemoryItem`**: The base Pydantic model tracking `strength` and `tier_level`.
- **`core.memory_manager.MemoryManager`**: Handles calculating tiers based on strength thresholds.
- **`core.resources.ResourceManager`**: A singleton to inject `LLM` and `Vector` databases safely.
- **`core.assembler.ItemAssembler`**: The central dispatcher routing items to specific algorithms.

## 📜 License

MIT License
