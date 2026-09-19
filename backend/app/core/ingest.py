"""M1 摄入/ETL。单一职责：把任意来源转成统一 Document 分片。
复用 pypdf / python-docx 解析；切片用稳定的递归字符窗口，无外部重依赖。
接口: ingest_text(text) -> List[Document]；ingest_file(path) -> List[Document]
"""
import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class Document:
    text: str
    source: str = "unknown"
    metadata: dict = field(default_factory=dict)


def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 80) -> List[str]:
    if chunk_size <= overlap:
        overlap = 0
    chunks: List[str] = []
    start = 0
    step = max(1, chunk_size - overlap)
    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        start += step
    return [c.strip() for c in chunks if c.strip()]


def ingest_text(
    text: str, source: str = "inline", chunk_size: int = 800, overlap: int = 80
) -> List[Document]:
    return [
        Document(text=c, source=source, metadata={"chunk_index": i})
        for i, c in enumerate(_chunk_text(text, chunk_size, overlap))
    ]


def ingest_file(path: str, chunk_size: int = 800, overlap: int = 80) -> List[Document]:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    ext = os.path.splitext(path)[1].lower()
    if ext in (".txt", ".md", ".json", ".csv", ".html"):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    elif ext == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(path)
        text = "\n".join((p.extract_text() or "") for p in reader.pages)
    elif ext == ".docx":
        from docx import Document as Docx

        text = "\n".join(p.text for p in Docx(path).paragraphs)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    return ingest_text(text, source=os.path.basename(path), chunk_size=chunk_size, overlap=overlap)
