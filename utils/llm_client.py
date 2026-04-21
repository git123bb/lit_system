import json
from openai import OpenAI
from anthropic import Anthropic
import config

class LLMClient:
    def __init__(self):
        self.provider = config.LLM_PROVIDER
        if self.provider == "openai":
            # 从 config 中读取千问的 base_url（如果没有则默认为 OpenAI 官方地址）
            base_url = getattr(config, "QWEN_BASE_URL", None)
            if base_url:
                # 使用千问兼容地址
                self.client = OpenAI(
                    api_key=config.OPENAI_API_KEY,
                    base_url=base_url
                )
                self.model = "qwen-plus"   # 可改为 qwen-turbo / qwen-max
            else:
                # 纯 OpenAI 官方
                self.client = OpenAI(api_key=config.OPENAI_API_KEY)
                self.model = "gpt-4o-mini"
        elif self.provider == "claude":
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