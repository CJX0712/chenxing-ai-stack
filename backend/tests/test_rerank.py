from app.core.rerank import Reranker


def test_none_mode_keeps_order_and_slices():
    r = Reranker()
    docs = ["a", "b", "c", "d"]
    assert r.rerank("q", docs) == docs
    assert r.rerank("q", docs, top_k=2) == ["a", "b"]
