"""API 层数据契约（Pydantic）。前后端、模块间以此为唯一接口定义。"""
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="用户提问")
    top_k: int = Field(5, ge=1, le=50, description="召回文档数")
    use_rag: bool = True


class ChatResponse(BaseModel):
    answer: str
    context: List[str] = []
    model: str = ""


class IngestTextRequest(BaseModel):
    text: str = Field(..., min_length=1)
    source: str = "inline"


class IngestFileResponse(BaseModel):
    ingested: int
    collection: str


class HealthResponse(BaseModel):
    status: str
    llm_mode: str
    embed_mode: str
    vector_mode: str
    rerank_mode: str
    auth_enabled: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
