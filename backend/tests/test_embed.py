import math

from app.core.embed import Embedder


def test_fake_embed_deterministic_and_normalized():
    e = Embedder()
    v1 = e.embed(["晨星是前端工程师"])[0]
    v2 = e.embed(["晨星是前端工程师"])[0]
    v3 = e.embed(["Pi Node 在 31401"])[0]
    assert len(v1) == e.s.embed_dim
    assert v1 == v2  # 确定性
    assert abs(math.sqrt(sum(x * x for x in v1)) - 1.0) < 1e-9  # 单位向量
    assert v1 != v3  # 不同文本不同向量


def test_embed_batch():
    e = Embedder()
    vs = e.embed(["a", "b", "c"])
    assert len(vs) == 3
