import json
import re
import threading
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, UploadFile

from incidentlens.config import ROOT
from incidentlens.models import Investigation, SearchRequest

router = APIRouter(prefix="/api")
mutation_lock = threading.RLock()


@router.get("/status")
def status(request: Request):
    p = request.app.state.pipeline
    return {
        "ready": bool(p.retriever.chunks),
        "chunks": len(p.retriever.chunks),
        "documents": len({c.document for c in p.retriever.chunks}),
        "relationships": len(p.graph.edges),
        "generator": p.cfg.generator,
        "embedding_model": p.cfg.embedding_model,
        "reranker_model": p.cfg.reranker_model,
        "pdf_parser": p.cfg.pdf_parser,
        "pii_ner": p.cfg.pii_ner,
        "llama_guard": bool(p.cfg.llama_guard_model),
        "scope": "local demo, synthetic documents, no live infrastructure access",
    }


@router.post("/investigate", response_model=Investigation)
def investigate(body: SearchRequest, request: Request):
    with mutation_lock:
        try:
            return request.app.state.pipeline.investigate(body)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        except (RuntimeError, OSError):
            raise HTTPException(503, "Local index or model is unavailable. Check setup.") from None


@router.get("/documents")
def documents(request: Request):
    p = request.app.state.pipeline
    items = {}
    for c in p.retriever.chunks:
        entry = items.setdefault(
            c.document,
            {"name": c.document, "title": c.title, "parser": c.parser, "chunks": 0, "pages": set()},
        )
        entry["chunks"] += 1
        if c.page:
            entry["pages"].add(c.page)
    return [{**x, "pages": sorted(x["pages"])} for x in items.values()]


@router.get("/source/{chunk_id}")
def source(chunk_id: str, request: Request):
    chunk = request.app.state.pipeline.retriever.chunk_map.get(chunk_id)
    if chunk is None:
        raise HTTPException(404, "Source passage not found")
    return chunk


@router.get("/graph")
def graph(request: Request):
    p = request.app.state.pipeline
    return {"nodes": list(p.graph.graph.nodes), "edges": p.graph.edges}


@router.get("/evaluations")
def evaluations():
    path = ROOT / "evaluation" / "results.json"
    return (
        json.loads(path.read_text())
        if path.exists()
        else {
            "status": "not_run",
            "message": "Run python scripts/evaluate.py to produce real results.",
        }
    )


@router.post("/upload")
def upload(file: UploadFile, request: Request):
    p = request.app.state.pipeline
    name = Path(file.filename or "document").name
    name = re.sub(r"[^a-zA-Z0-9_.-]", "-", name)[:100]
    if Path(name).suffix.lower() not in {".pdf", ".md", ".txt", ".csv"}:
        raise HTTPException(415, "Supported uploads: PDF, Markdown, TXT, CSV")
    data = file.file.read(5 * 1024 * 1024 + 1)
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(413, "Upload exceeds 5 MB")
    if not data:
        raise HTTPException(422, "Empty document")
    if name.endswith(".pdf") and not data.startswith(b"%PDF-"):
        raise HTTPException(415, "Invalid PDF signature")
    target = p.cfg.corpus_dir / name
    with mutation_lock:
        if target.exists():
            raise HTTPException(409, "A document with this name already exists")
        target.write_bytes(data)
        try:
            p.build()
        except Exception:
            target.unlink(missing_ok=True)
            raise HTTPException(422, "Document could not be parsed or indexed") from None
    return {"document": name, "chunks": len(p.retriever.chunks), "guardrails": p.ingestion_findings}
