from app.core.llm import LLM


def test_fake_includes_query():
    out = LLM().generate([{"role": "user", "content": "晨星是谁"}])
    assert "晨星是谁" in out
    assert out.startswith("[FAKE:")
