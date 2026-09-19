"""测试夹具：固定 fake/memory 模式，保证无 Ollama/Qdrant 也能独立验证每个模块。"""
import os

os.environ.setdefault("LLM_MODE", "fake")
os.environ.setdefault("EMBED_MODE", "fake")
os.environ.setdefault("VECTOR_MODE", "memory")
os.environ.setdefault("RERANK_MODE", "none")
os.environ.setdefault("AUTH_ENABLED", "false")
os.environ.setdefault("OTEL_ENABLED", "false")

import pytest
from fastapi.testclient import TestClient

from app.core.rag import get_rag
from app.main import app


@pytest.fixture
def client():
    get_rag.cache_clear()
    yield TestClient(app)
