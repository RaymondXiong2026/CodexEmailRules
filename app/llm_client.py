from __future__ import annotations

import json
from typing import Any

from simple_openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_fixed


class LLMClient:
    def __init__(self, api_key: str, base_url: str, model: str, timeout: int):
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        self.model = model

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def json_chat(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        content = resp.choices[0].message.content
        return json.loads(content)
