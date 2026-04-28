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

- **Multi-Tier Degradation:** Automatically handles the decay of unused memory and the promotion of actively used memory (Supports standard linear decay, Ebbinghaus Forgetting Curve, LRU, LFU, and Volatile memory).
- **Resource Decoupling:** Pluggable `VectorResource` and `LLMResource` abstractions.
- **22+ Built-in Algorithms:** Define custom behaviors via `AssemblyAlgorithm`. PowerStyle ships with algorithms for vector search, keyword matching, Jaccard similarity, metadata filtering, length truncation, semantic summarization, and more.
- **Zero Business Logic:** PowerStyle knows nothing about your business models. Simply inherit from `MemoryItem` and let the `MemoryManager` and `ItemAssembler` do the heavy lifting.

## 🧠 Memory Decay Managers
PowerStyle allows you to choose how your agent's memory degrades over time by utilizing different `MemoryManager` classes:
1. **`MemoryManager` (Default):** Linear decay. Memory strength drops by a fixed amount every day.
2. **`EbbinghausMemoryManager`:** Exponential decay ($R = e^{-t/S}$). Simulates the human brain's forgetting curve, where old but deeply ingrained memories decay slowly, but new unreinforced memories decay rapidly.
3. **`LRUMemoryManager`:** Least Recently Used. A strict cutoff; if a memory isn't accessed within `N` days, its strength drops to 0 instantly.
4. **`FrequencyMemoryManager` (LFU):** Least Frequently Used. Decay rate is inversely proportional to total access count. Highly referenced memories become "stubborn" and resist decay.
5. **`VolatileMemoryManager`:** Aggressive decay similar to RAM. Drops rapidly overnight, suited for short-lived session contexts.

## 🧩 The 22+ Assembly Algorithms
When assembling the context for your LLM, PowerStyle routes the items through specific algorithms. Here is a breakdown of the standard library:

### Retrieval & Matching
- **`ExactMatchAlgorithm`**: Filters items using a custom lambda function.
- **`VectorSearchAlgorithm`**: Uses embedding vectors to find semantic similarity (Top K).
- **`KeywordMatchAlgorithm`**: Fast, lightweight string-inclusion matching.
- **`JaccardSimilarityAlgorithm`**: Token-level set intersection matching for local, DB-free comparisons.
- **`TitleMatchAlgorithm` & `RegexMatchAlgorithm`**: Text-specific precision targeting.

### Sorting & Prioritization
- **`TimeWeightSortAlgorithm`**: Sorts by a weighted formula of Recency (30%) + Strength (70%). Perfect for chat histories.
- **`StrengthSortAlgorithm`**: Pure descending sort by memory strength.
- **`RecencySortAlgorithm`**: Pure descending sort by last access time.
- **`LengthSortAlgorithm`**: Sorts items by token/character length.

### Truncation & Slicing
- **`LengthTruncateAlgorithm`**: Hard limit truncation. Stops appending items once the total character count exceeds the LLM context window size.
- **`FirstNAlgorithm` & `LastNAlgorithm`**: Standard head/tail slicing.

### Filtering & Metadata
- **`MetadataFilterAlgorithm` & `MetadataSortAlgorithm`**: Targets specific structured keys stored in the memory's `metadata` dict.
- **`TierFilterAlgorithm` & `ScoreThresholdAlgorithm`**: Slices memory strictly by its tier or strength score limit.
- **`CategoryGroupAlgorithm`**: Groups by category and only takes the top 1 from each group.
- **`DeduplicationAlgorithm`**: Removes identical text contents.

### Generative & Transformation
- **`LLMSummaryAlgorithm`**: Passes a large list of low-tier memories into an LLM to generate a lossy, highly compressed summary text block.
- **`RandomSampleAlgorithm`**: Randomly samples N items (useful for breaking LLM determinism or increasing creativity).
- **`ShuffleAlgorithm`**: Shuffles the final list to prevent "Lost in the Middle" LLM position bias.

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
