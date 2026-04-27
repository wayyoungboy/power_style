import json
from typing import Dict, Any, Optional
from openai import OpenAI
from power_style.core.resources import LLMResource

class OpenAILLMResource(LLMResource):
    """OpenAI 的 LLM 资源实现"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", base_url: Optional[str] = None):
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = OpenAI(**kwargs)
        self.model = model

    def generate(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """调用 OpenAI 生成内容"""
        messages = [{"role": "user", "content": prompt}]
        
        # 如果上下文中包含 system_prompt，则将其加入
        if context and "system_prompt" in context:
            messages.insert(0, {"role": "system", "content": context["system_prompt"]})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2048
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"Error calling OpenAI: {str(e)}"
