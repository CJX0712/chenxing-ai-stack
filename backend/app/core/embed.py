"""M2 向量化。单一职责：文本 -> 向量。
real 模式复用 Ollama /api/embed（免 sentence-transformers 重依赖）；
fake 模式产出确定性哈希向量，保证无模型环境也能独立验证与单测。
接口: embed(texts: List[str]) -> List[List[float]]
"""
import hashlib
import math

import httpx

from app.config import get_settings


class Embedder:
    def __init__(self, settings=None):
        self.s = settings or get_settings()

    def embed(self, texts: list) -> list:
        if self.s.embed_mode == "real":
            return self._embed_ollama(texts)
        return [self._fake(t) for t in texts]

    def _embed_ollama(self, texts: list) -> list:
        url = f"{self.s.ollama_base_url}/api/embed"
        resp = httpx.post(
            url, json={"model": self.s.embed_model, "input": texts}, timeout=60
        )
        resp.raise_for_status()
        return resp.json()["embeddings"]

    def _fake(self, text: str) -> list:
        dim = self.s.embed_dim
        h = hashlib.sha256(text.encode("utf-8")).digest()
        vec = [(h[i % len(h)] / 255.0) for i in range(dim)]
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]
