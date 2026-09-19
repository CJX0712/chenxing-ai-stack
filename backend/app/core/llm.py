"""M5 LLM 推理。单一职责：多轮消息 -> 文本补全。
real 模式复用 Ollama OpenAI 兼容 /api/chat；fake 模式返回确定性占位，保证链路可独立验证。
接口: generate(messages: List[dict]) -> str
"""
import httpx

from app.config import get_settings


class LLM:
    def __init__(self, settings=None):
        self.s = settings or get_settings()

    def generate(self, messages: list) -> str:
        if self.s.llm_mode == "real":
            return self._generate_ollama(messages)
        return self._fake(messages)

    def _generate_ollama(self, messages: list) -> str:
        url = f"{self.s.ollama_base_url}/api/chat"
        resp = httpx.post(
            url,
            json={"model": self.s.llm_model, "messages": messages, "stream": False},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]

    def _fake(self, messages: list) -> str:
        last = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last = m.get("content", "")
                break
        return f"[FAKE:{self.s.llm_model}] 针对「{last}」的占位回答（未接入真实模型）。"
