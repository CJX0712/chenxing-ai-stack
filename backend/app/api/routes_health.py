from fastapi import APIRouter

from app.config import get_settings
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health():
    s = get_settings()
    return HealthResponse(
        status="ok",
        llm_mode=s.llm_mode,
        embed_mode=s.embed_mode,
        vector_mode=s.vector_mode,
        rerank_mode=s.rerank_mode,
        auth_enabled=s.auth_enabled,
    )
