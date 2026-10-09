from typing import Literal

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    id: str
    document: str
    title: str
    section: str
    page: int | None = None
    text: str
    parser: str
    entities: list[str] = Field(default_factory=list)


class Hit(BaseModel):
    chunk: Chunk
    score: float
    vector_rank: int | None = None
    keyword_rank: int | None = None
    initial_rank: int = 0
    rerank_score: float | None = None


class SearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=2000)
    mode: Literal["vector", "hybrid", "reranked"] = "reranked"
    top_k: int = Field(default=4, ge=1, le=8)
    hyde: bool = False


class Finding(BaseModel):
    kind: str
    action: str
    count: int = 1


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str
    chunk_id: str
    document: str
    page: int | None = None
    evidence: str


class AnswerClaim(BaseModel):
    text: str = Field(min_length=1, max_length=1200)
    citations: list[str] = Field(min_length=1, max_length=8)


class GeneratedAnswer(BaseModel):
    claims: list[AnswerClaim] = Field(max_length=6)


class Investigation(BaseModel):
    query: str
    status: Literal["answered", "insufficient_evidence", "blocked", "generator_unavailable"]
    answer: str
    claims: list[AnswerClaim] = Field(default_factory=list)
    hits: list[Hit] = Field(default_factory=list)
    candidates: list[Hit] = Field(default_factory=list)
    graph: list[GraphEdge] = Field(default_factory=list)
    guardrails: list[Finding] = Field(default_factory=list)
    timings_ms: dict[str, float] = Field(default_factory=dict)
    generator: str
    mode: str
    hyde_used: bool = False
