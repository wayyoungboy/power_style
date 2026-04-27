from pydantic import BaseModel, Field
from typing import Dict, Any, List

class VectorConfig(BaseModel):
    provider: str = "seekdb"
    embedding_model: str = "text-embedding-3-small"
    dimensions: int = 1536
    top_k_default: int = 5
    similarity_threshold: float = 0.75

class PromptConfig(BaseModel):
    # 用户自定义提示词
    judge_prompt: str = (
        "You are an evaluator. Determine if the input is a valid coding style rule.\n"
        "Input: {input}"
    )
    summarize_prompt: str = (
        "Summarize the following archived rules into a general guideline:\n"
        "{rules_text}"
    )
    format_prompt: str = (
        "Format the input into a structured rule with title, content, category."
    )

class TierConfig(BaseModel):
    level: int
    name: str
    threshold: float
    algorithm: str

class FrameworkConfig(BaseModel):
    vector: VectorConfig = Field(default_factory=VectorConfig)
    prompts: PromptConfig = Field(default_factory=PromptConfig)
    
    # 支持无限层级，默认配置为三层
    tiers: List[TierConfig] = Field(default_factory=lambda: [
        TierConfig(level=1, name="L1_CORE", threshold=0.8, algorithm="exact_match"),
        TierConfig(level=2, name="L2_NORMAL", threshold=0.3, algorithm="vector_search"),
        TierConfig(level=3, name="L3_ARCHIVE", threshold=0.0, algorithm="llm_summary"),
    ])
    
    decay_rate_per_day: float = 0.05
    promotion_boost: float = 0.15

# 全局默认配置
default_config = FrameworkConfig()
