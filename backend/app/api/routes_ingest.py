import os
import tempfile

from fastapi import APIRouter, File, UploadFile

from app.core.ingest import ingest_file, ingest_text
from app.core.rag import get_rag
from app.schemas import IngestFileResponse, IngestTextRequest

router = APIRouter(prefix="/v1", tags=["ingest"])


@router.post("/ingest", response_model=IngestFileResponse)
def ingest_text_endpoint(req: IngestTextRequest):
    docs = ingest_text(req.text, source=req.source)
    n = get_rag().add_documents([d.text for d in docs], [d.source for d in docs])
    return IngestFileResponse(ingested=n, collection=get_rag().store.s.qdrant_collection)


@router.post("/ingest/file", response_model=IngestFileResponse)
def ingest_file_endpoint(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename or "")[1] or ".txt"
    with tempfile.NamedTemporaryFile("wb", suffix=suffix, delete=False) as tmp:
        tmp.write(file.file.read())
        path = tmp.name
    try:
        docs = ingest_file(path)
    finally:
        os.unlink(path)
    n = get_rag().add_documents([d.text for d in docs], [d.source for d in docs])
    return IngestFileResponse(ingested=n, collection=get_rag().store.s.qdrant_collection)
