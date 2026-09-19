"""全局配置（版本锁定 + 12-factor）。所有模块通过 get_settings() 读取，单一事实来源。"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "Chenxing AI Stack"
    app_version: str = "1.0.0"

    # --- LLM 推理 (M5) ---
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "qwen2.5:7b"
    llm_mode: str = "fake"  # fake | real（real 走 Ollama /v1/chat/completions）

    # --- 向量化 (M2) ---
    embed_model: str = "nomic-embed-text"
    embed_mode: str = "fake"  # fake | real（real 走 Ollama /api/embed）
    embed_dim: int = 768

    # --- 向量库 (M3) ---
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "chenxing_docs"
    vector_mode: str = "memory"  # memory | qdrant

    # --- 重排 (M4) ---
    rerank_mode: str = "none"  # none | cross-encoder

    # --- 鉴权 ---
    auth_enabled: bool = False
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # --- 服务 ---
    host: str = "0.0.0.0"
    port: int = 8000

    # --- 可观测 (M8) ---
    otel_enabled: bool = False
    otel_endpoint: str = "http://localhost:4317"


@lru_cache
def get_settings() -> Settings:
    return Settings()
