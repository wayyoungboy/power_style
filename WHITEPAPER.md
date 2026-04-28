# PowerStyle: A Dynamic Multi-Tier Memory Degradation and Routing Framework for Large Language Models

**Abstract**
As Large Language Models (LLMs) are increasingly deployed in persistent, long-running agentic environments, managing context windows efficiently has become a critical challenge. Retaining all historical interactions leads to context explosion, increased latency, and hallucination via distraction, while aggressive truncation results in catastrophic forgetting. In this paper, we introduce **PowerStyle**, a decoupled, un-opinionated memory management framework. PowerStyle applies a novel multi-tier degradation mechanism inspired by the Ebbinghaus Forgetting Curve to simulate human-like cognitive fading. By decoupling memory tracking from the specific domain (e.g., coding guidelines, chat history), and exposing a generic `ItemAssembler` with 22+ pluggable algorithmic strategies (including Vector Semantic Search, Jaccard Similarity, and LLM Summarization), PowerStyle provides a scalable solution to the LLM memory lifecycle problem.

---

## 1. Introduction
Modern LLM-based autonomous agents face a fundamental bottleneck: the rigid, stateless nature of their prompt-based context windows. Existing solutions often fall into two extremes: 
1. **Naive sliding windows**, which rigidly slice off the oldest context regardless of its importance.
2. **Pure vector databases (RAG)**, which retrieve top-k semantic matches but often fail to prioritize temporally relevant context (e.g., an instruction given by the user 5 seconds ago versus one given 5 days ago).

To address these shortcomings, we propose **PowerStyle**, an open-source Python framework designed to manage the full lifecycle of an agent's memory. PowerStyle shifts the paradigm from "passive storage" to "active cognitive degradation".

## 2. Architecture & Methodology
PowerStyle's architecture is strictly decoupled from business logic. Any Python object inheriting from the base `MemoryItem` class can be managed by the system. The framework consists of three core pillars:

### 2.1 Multi-Tier Degradation Engine (`MemoryManager`)
Memory items in PowerStyle possess a continuous scalar `strength` $\in [0, 1]$ and a `last_accessed` timestamp. The framework classifies memory into discrete Tiers (by default: `L1_CORE`, `L2_NORMAL`, `L3_ARCHIVE`). 
- **Promotion (Reinforcement):** Accessing or actively using a memory item triggers a `promote()` call, injecting a `promotion_boost` and upgrading its tier.
- **Demotion (Decay):** Over time, memory strength decays. PowerStyle supports both linear decay ($\Delta S = -\alpha \Delta t$) and **Ebbinghaus Exponential Decay** ($S_t = S_0 \cdot e^{-t / \lambda}$), simulating the natural fading of human memory. Memories that drop below specific thresholds are demoted to lower tiers.

### 2.2 Algorithmic Item Assembly (`ItemAssembler`)
When an Agent needs to construct its context prompt, the `ItemAssembler` routes the request through different algorithmic pipelines based on the memory's tier:
- **Tier 1 (High Strength / Recent):** Routed via `ExactMatchAlgorithm` or `TimeWeightSortAlgorithm`, guaranteeing inclusion with 100% precision.
- **Tier 2 (Moderate Strength):** Routed via `VectorSearchAlgorithm` or `JaccardSimilarityAlgorithm` to semantically match current queries, ensuring only relevant past context is loaded.
- **Tier 3 (Archived / Weak):** Routed via `LLMSummaryAlgorithm`, which compresses raw historical data into dense summaries to save token space.

### 2.3 Resource Decoupling
To ensure maximum flexibility, external dependencies are abstracted:
- `VectorResource`: Interface for vector storage (e.g., SeekDB, Chroma, Pinecone).
- `LLMResource`: Interface for model invocation (e.g., OpenAI API, Local Ollama).

## 3. Standard Library: The 22+ Algorithms
A framework's utility is defined by its extensibility. PowerStyle ships with over 22 built-in `AssemblyAlgorithm` plugins, including:
* **Context Protection:** `LengthTruncateAlgorithm` strictly bounds the concatenated output size to prevent context window overflow.
* **Exploration vs Exploitation:** `RandomSampleAlgorithm` injects controlled chaos, allowing agents to "remember" tangential facts and spark creative correlations.
* **Fallback Mechanisms:** `KeywordMatchAlgorithm` provides lightweight lexical routing when Vector databases are offline or overkill.

## 4. Use Cases
1. **Chatbots & Companions:** Preserving persona continuity over months of interaction using the Ebbinghaus Manager.
2. **Coding Agents:** Prioritizing newly defined project conventions (Tier 1) over globally established, less frequently relevant coding rules (Tier 2).

## 5. Conclusion
PowerStyle successfully maps human cognitive memory structures—short-term focus, associative long-term memory, and lossy compression—onto the deterministic context windows of Large Language Models. By formalizing memory management into generic tiers and pluggable algorithms, it significantly lowers the barrier for developing robust, context-aware AI agents.

---
*Source Code: [wayyoungboy/power_style](https://github.com/wayyoungboy/power_style)*
