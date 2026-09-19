"""M3 向量库。单一职责：向量存取与相似检索。
复用 Qdrant；memory 模式用 :memory: 客户端，无需外部服务即可单测验证。
接口: upsert(docs, vectors) / search(vector, top_k) -> List[Hit]
"""
import hashlib
from dataclasses import dataclass
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import get_settings


@dataclass
class Hit:
    text: str
    source: str
    score: float


def _stable_id(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)


class VectorStore:
    def __init__(self, settings=None):
        self.s = settings or get_settings()
        if self.s.vector_mode == "memory":
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(url=self.s.qdrant_url)
        self._ensure()

    def _ensure(self):
        name = self.s.qdrant_collection
        if not self.client.collection_exists(name):
            self.client.create_collection(
                name,
                vectors_config=VectorParams(
                    size=self.s.embed_dim, distance=Distance.COSINE
                ),
            )

    def upsert(self, docs: list, vectors: list, sources: list = None):
        sources = sources or ["unknown"] * len(docs)
        points = [
            PointStruct(
                id=_stable_id(d),
                vector=v,
                payload={"text": d, "source": sources[i]},
            )
            for i, (d, v) in enumerate(zip(docs, vectors))
        ]
        self.client.upsert(self.s.qdrant_collection, points=points)
        return len(points)

    def search(self, vector: list, top_k: int = 5) -> List[Hit]:
        res = self.client.query_points(
            self.s.qdrant_collection, query=vector, limit=top_k
        )
        return [
            Hit(text=p.payload["text"], source=p.payload.get("source", ""), score=p.score)
            for p in res.points
        ]

    def count(self) -> int:
        return self.client.count(self.s.qdrant_collection).count
