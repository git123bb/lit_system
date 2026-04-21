import json
from openai import OpenAI
# 移除顶层的 anthropic 导入，避免未安装时模块加载失败
import config

class LLMClient:
    def __init__(self):
        self.provider = config.LLM_PROVIDER
        if self.provider == "openai":
            # 兼容千问的 OpenAI 接口
            base_url = getattr(config, "QWEN_BASE_URL", None)
            if base_url:
                self.client = OpenAI(
                    api_key=config.OPENAI_API_KEY,
                    base_url=base_url
                )
                self.model = "qwen-plus"
            else:
                self.client = OpenAI(api_key=config.OPENAI_API_KEY)
                self.model = "gpt-4o-mini"
        elif self.provider == "claude":
            # 延迟导入 anthropic，仅当真正使用时才加载
            from anthropic import Anthropic
            self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
            self.model = "claude-3-haiku-20240307"
        else:
            self.client = OpenAI(base_url=config.LOCAL_LLM_URL, api_key="not-needed")
            self.model = "local-model"

    def generate(self, prompt, system_prompt="You are a helpful research assistant."):
        if self.provider == "claude":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            return response.choices[0].message.content
