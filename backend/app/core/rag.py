"""RAG 组合层：把 M2 向量化 + M3 向量库 + M4 重排拼成完整检索链路。
对外只暴露 add_documents / retrieve 两个接口，供编排层(M6)与 API 调用。
"""
from functools import lru_cache

from app.core.embed import Embedder
from app.core.rerank import Reranker
from app.core.vector_store import VectorStore


@lru_cache
def get_rag():
    """进程级单例：memory 模式下向量库跨请求持久，避免每次请求重建空库。"""
    return RAG()


class RAG:
    def __init__(self, embedder=None, store=None, reranker=None):
        self.embedder = embedder or Embedder()
        self.store = store or VectorStore()
        self.reranker = reranker or Reranker()

    def add_documents(self, docs: list, sources: list = None) -> int:
        vectors = self.embedder.embed(docs)
        return self.store.upsert(docs, vectors, sources)

    def retrieve(self, query: str, top_k: int = 5) -> list:
        qv = self.embedder.embed([query])[0]
        hits = self.store.search(qv, top_k=max(top_k * 3, 3))
        docs = [h.text for h in hits]
        return self.reranker.rerank(query, docs, top_k)
