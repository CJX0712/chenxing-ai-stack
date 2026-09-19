from app.core.embed import Embedder
from app.core.vector_store import VectorStore


def test_memory_store_upsert_search():
    store = VectorStore()
    embedder = Embedder()
    docs = ["晨星在深圳", "Pi Node 端口 31401", "企业协同平台 v3.2"]
    vecs = embedder.embed(docs)
    n = store.upsert(docs, vecs)
    assert n == 3
    assert store.count() == 3
    hits = store.search(embedder.embed(["深圳 晨星"])[0], top_k=2)
    assert len(hits) == 2
    assert hits[0].text
    assert isinstance(hits[0].score, float)
