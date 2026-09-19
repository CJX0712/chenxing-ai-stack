from app.core.orchestrator import run
from app.core.rag import get_rag


def test_run_without_rag():
    out = run("你好", use_rag=False)
    assert out["answer"]
    assert out["context"] == []


def test_run_with_rag_retrieves_context():
    get_rag.cache_clear()
    rag = get_rag()
    rag.add_documents(
        ["晨星是深圳的前端工程师，负责企业协同平台 v3.2。", "Pi Node 容器端口 31401。"]
    )
    out = run("晨星负责什么", top_k=2)
    assert out["context"], "应召回非空上下文"
    assert out["answer"]
