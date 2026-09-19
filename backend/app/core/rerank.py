"""M4 重排。单一职责：对召回结果按相关性再排序。
none 模式保留原序（MVP 可跑）；cross-encoder 模式懒加载 bge-reranker，避免重依赖拖累安装与启动。
接口: rerank(query, docs, top_k) -> List[str]
"""
from app.config import get_settings


class Reranker:
    def __init__(self, settings=None):
        self.s = settings or get_settings()
        self._model = None

    def rerank(self, query: str, docs: list, top_k: int = None) -> list:
        if self.s.rerank_mode == "cross-encoder":
            docs = self._ce(query, docs)
        if top_k:
            docs = docs[:top_k]
        return docs

    def _ce(self, query: str, docs: list) -> list:
        if self._model is None:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder("BAAI/bge-reranker-v2-m3")
        pairs = [(query, d) for d in docs]
        scores = self._model.predict(pairs)
        return [d for _, d in sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)]
