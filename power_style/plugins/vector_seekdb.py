from typing import List, Dict, Any
from power_style.core.resources import VectorResource
from server.db import get_db

class SeekDBVectorResource(VectorResource):
    """SeekDB 的向量库资源真实实现，接入全局 DB"""
    
    def __init__(self, collection_name: str = "style_rules_search"):
        self.collection_name = collection_name

    def search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """调用全局 SeekDB 进行语义搜索"""
        db = get_db()
        results = db.search_by_content(query, limit=top_k)
        return [{"id": str(r["id"]), "text": r.get("content", ""), "metadata": r} for r in results]

    def add(self, item_id: str, text: str, metadata: Dict[str, Any] = None):
        """将文本与元数据存入 SeekDB"""
        db = get_db()
        # id 通常是数字，但 generic 中是 str，所以要做转换
        if str(item_id).isdigit():
            db.add_to_search_index(int(item_id), metadata.get("title", "") if metadata else "", text, metadata or {})
