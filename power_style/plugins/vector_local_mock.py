from typing import List, Dict, Any, Optional
from power_style.core.resources import VectorResource
import math

class LocalMockVectorResource(VectorResource):
    """一个简单的内存级 Mock 向量资源，用于测试和演示。
    它使用简单的 Jaccard 相似度/词频统计代替真正的向量计算。
    """
    def __init__(self):
        # 存储结构: item_id -> {"text": str, "metadata": dict}
        self.store: Dict[str, Dict[str, Any]] = {}

    def add(self, item_id: str, text: str, metadata: Optional[Dict[str, Any]] = None):
        self.store[item_id] = {
            "text": text,
            "metadata": metadata or {}
        }

    def _calculate_similarity(self, query: str, text: str) -> float:
        """简单的相似度计算：按空格分词的词语重合度 (Jaccard similarity)"""
        if not query or not text:
            return 0.0
        
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        
        if not query_words or not text_words:
            return 0.0
            
        intersection = query_words.intersection(text_words)
        union = query_words.union(text_words)
        
        return len(intersection) / len(union)

    def search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        results = []
        for item_id, data in self.store.items():
            score = self._calculate_similarity(query, data["text"])
            if score > 0:
                results.append({
                    "id": item_id,
                    "score": score,
                    "text": data["text"],
                    "metadata": data["metadata"]
                })
        
        # 按分数降序排列
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
