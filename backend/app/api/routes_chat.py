from fastapi import APIRouter, Depends

from app.config import get_settings
from app.core.orchestrator import run as orchestrate
from app.schemas import ChatRequest, ChatResponse
from app.security import verify_token

router = APIRouter(prefix="/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, user: str = Depends(verify_token)):
    out = orchestrate(req.query, top_k=req.top_k, use_rag=req.use_rag)
    return ChatResponse(
        answer=out["answer"], context=out["context"], model=get_settings().llm_model
    )
