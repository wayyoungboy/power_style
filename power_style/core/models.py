from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

class MemoryItem(BaseModel):
    """泛型化：通用的多层级记忆载体基类"""
    id: str
    content: str  # 核心内容（可以是代码规则、聊天记录、知识点片段等）
    
    # 记忆与层级核心属性
    strength: float = Field(default=0.5, description="强度/重要性 (0.0 - 1.0)")
    tier_level: int = Field(default=2, description="当前层级编号（层数不限，数字越小优先级越高）")
    last_accessed: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # 业务扩展元数据（用于实现不同的特化逻辑，存放额外字段）
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CodeStyleItem(MemoryItem):
    """【特化示例1】代码风格规则"""
    title: str = "Untitled"
    category: str = "general"
    project_type: str = "all"
    tags: List[str] = Field(default_factory=list)

class ChatHistoryItem(MemoryItem):
    """【特化示例2】对话记忆/上下文"""
    session_id: str = "default"
    role: str = "user"
