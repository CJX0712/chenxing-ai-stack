from app.core.ingest import ingest_file, ingest_text


def test_ingest_text_chunks():
    text = "晨星在深圳做前端。" * 50
    docs = ingest_text(text, source="t", chunk_size=100, overlap=20)
    assert len(docs) > 1
    assert all(d.text.strip() for d in docs)
    assert docs[0].metadata["chunk_index"] == 0


def test_ingest_file_md(tmp_path):
    p = tmp_path / "a.md"
    p.write_text("# 标题\n晨星负责企业协同平台 v3.2。", encoding="utf-8")
    docs = ingest_file(str(p))
    assert docs and "晨星" in docs[0].text
    assert docs[0].source == "a.md"


def test_ingest_unsupported(tmp_path):
    p = tmp_path / "a.xyz"
    p.write_text("x", encoding="utf-8")
    try:
        ingest_file(str(p))
        assert False, "should raise"
    except ValueError:
        pass
