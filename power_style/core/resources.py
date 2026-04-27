from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class LLMResource(ABC):
    """抽象的 LLM 资源接口"""
    @abstractmethod
    def generate(self, prompt: str, context: Dict[str, Any] = None) -> str:
        pass

class VectorResource(ABC):
    """抽象的向量检索资源接口"""
    @abstractmethod
    def search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def add(self, item_id: str, text: str, metadata: Dict[str, Any] = None):
        pass

class ResourceManager:
    """资源统一调度与管理器"""
    def __init__(self):
        self._llms: Dict[str, LLMResource] = {}
        self._vectors: Dict[str, VectorResource] = {}
        
        self.default_llm: Optional[str] = None
        self.default_vector: Optional[str] = None

    def register_llm(self, name: str, resource: LLMResource, set_default: bool = False):
        self._llms[name] = resource
        if set_default or self.default_llm is None:
            self.default_llm = name

    def register_vector(self, name: str, resource: VectorResource, set_default: bool = False):
        self._vectors[name] = resource
        if set_default or self.default_vector is None:
            self.default_vector = name

    def get_llm(self, name: Optional[str] = None) -> Optional[LLMResource]:
        target_name = name or self.default_llm
        if not target_name or target_name not in self._llms:
            return None
        return self._llms[target_name]

    def get_vector(self, name: Optional[str] = None) -> Optional[VectorResource]:
        target_name = name or self.default_vector
        if not target_name or target_name not in self._vectors:
            return None
        return self._vectors[target_name]

# 全局单例的资源调度器
resource_manager = ResourceManager()
