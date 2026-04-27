from typing import Dict, Any
from power_style.core.resources import LLMResource

class LocalMockLLMResource(LLMResource):
    """
    一个本地兜底的模拟 LLM 资源，不依赖任何网络调用。
    用于在断网环境中测试“优雅降级”特性，或为接入未来的本地模型(如 Ollama / llama.cpp) 提供示例。
    """
    def generate(self, prompt: str, context: Dict[str, Any] = None) -> str:
        # 这里你可以实际接入类似 llama.cpp 的 Python SDK 或者本地运行的规则引擎
        
        # 目前我们仅仅简单返回带有前缀的信息，模拟已处理
        return f"[Local Offline Model] 已离线处理！源文本长度: {len(prompt)} 字符。"
