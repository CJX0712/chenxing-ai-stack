def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["llm_mode"] == "fake"


def test_ingest_then_chat(client):
    r = client.post(
        "/v1/ingest",
        json={"text": "晨星负责企业协同平台 v3.2 的 React 组件重构。", "source": "t"},
    )
    assert r.status_code == 200
    assert r.json()["ingested"] >= 1

    r2 = client.post("/v1/chat", json={"query": "晨星负责什么", "top_k": 3})
    assert r2.status_code == 200
    body = r2.json()
    assert body["answer"]
    assert body["context"], "RAG 应召回上下文"
