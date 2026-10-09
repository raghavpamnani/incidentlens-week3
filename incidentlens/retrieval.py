import json
import re
import threading
import uuid
from difflib import SequenceMatcher

from qdrant_client import QdrantClient, models
from rank_bm25 import BM25Okapi

from incidentlens.config import Settings
from incidentlens.models import Chunk, Hit


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:[-_][a-z0-9]+)*", text.lower())


def fuse(vector: list[str], keyword: list[str], constant: int = 60) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for ranking in (vector, keyword):
        for rank, chunk_id in enumerate(ranking, 1):
            scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (constant + rank)
    return sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))


def deduplicate(hits: list[Hit], threshold: float = 0.88) -> list[Hit]:
    unique = []
    for hit in hits:
        if not any(
            SequenceMatcher(None, hit.chunk.text.lower(), other.chunk.text.lower()).ratio()
            >= threshold
            for other in unique
        ):
            unique.append(hit)
    return unique


class Retriever:
    def __init__(self, cfg: Settings):
        self.cfg = cfg
        self.embedder = None
        self.reranker = None
        self.client = None
        self.chunks: list[Chunk] = []
        self.lock = threading.RLock()
        self.chunk_map: dict[str, Chunk] = {}
        self.bm25 = None

    def load_models(self):
        from sentence_transformers import CrossEncoder, SentenceTransformer

        if self.embedder is None:
            self.embedder = SentenceTransformer(
                self.cfg.embedding_model, device="cpu", cache_folder=str(self.cfg.model_dir)
            )
        if self.reranker is None:
            self.reranker = CrossEncoder(
                self.cfg.reranker_model,
                device="cpu",
                cache_folder=str(self.cfg.model_dir),
                max_length=512,
            )

    def index(self, chunks: list[Chunk]):
        if not chunks:
            raise ValueError("No safe, nonempty chunks to index")
        with self.lock:
            self.load_models()
            vectors = self.embedder.encode(
                [c.section + "\n" + c.text for c in chunks],
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            if self.client is None:
                self.client = QdrantClient(path=str(self.cfg.data_dir / "qdrant"))
            if self.client.collection_exists("incidents"):
                self.client.delete_collection("incidents")
            self.client.create_collection(
                "incidents",
                vectors_config=models.VectorParams(
                    size=len(vectors[0]), distance=models.Distance.COSINE
                ),
            )
            self.client.upsert(
                "incidents",
                points=[
                    models.PointStruct(
                        id=str(uuid.uuid5(uuid.NAMESPACE_URL, c.id)),
                        vector=v.tolist(),
                        payload={"chunk_id": c.id},
                    )
                    for c, v in zip(chunks, vectors)
                ],
                wait=True,
            )
            self.chunks = chunks
            self.chunk_map = {c.id: c for c in chunks}
            self.bm25 = BM25Okapi([tokens(c.section + " " + c.text) for c in chunks])
            (self.cfg.data_dir / "chunks.json").write_text(
                json.dumps([c.model_dump() for c in chunks], indent=2)
            )
            (self.cfg.data_dir / "index_config.json").write_text(
                json.dumps(
                    {
                        "embedding_model": self.cfg.embedding_model,
                        "reranker_model": self.cfg.reranker_model,
                        "chunk_count": len(chunks),
                    },
                    indent=2,
                )
            )

    def load(self):
        with self.lock:
            path = self.cfg.data_dir / "chunks.json"
            if not path.exists():
                return
            manifest = json.loads((self.cfg.data_dir / "index_config.json").read_text())
            if manifest["embedding_model"] != self.cfg.embedding_model:
                raise RuntimeError("Embedding configuration changed. Rebuild the index.")
            self.chunks = [Chunk.model_validate(c) for c in json.loads(path.read_text())]
            self.chunk_map = {c.id: c for c in self.chunks}
            self.bm25 = BM25Okapi([tokens(c.section + " " + c.text) for c in self.chunks])
            self.client = QdrantClient(path=str(self.cfg.data_dir / "qdrant"))

    def search(
        self, query: str, mode: str, top_k: int, vector_query: str | None = None
    ) -> tuple[list[Hit], list[Hit]]:
        with self.lock:
            if not self.chunks or self.client is None:
                raise RuntimeError("Index is not ready. Run scripts/build_index.py first.")
            self.load_models()
            vector = self.embedder.encode(vector_query or query, normalize_embeddings=True)
            found = self.client.query_points("incidents", query=vector.tolist(), limit=16).points
            vector_ids = [p.payload["chunk_id"] for p in found]
            similarities = {p.payload["chunk_id"]: p.score for p in found}
            kw_scores = self.bm25.get_scores(tokens(query))
            keyword_ids = [
                self.chunks[i].id
                for i in sorted(range(len(kw_scores)), key=lambda i: kw_scores[i], reverse=True)[
                    :16
                ]
                if kw_scores[i] > 0
            ]
            ranked = (
                [(i, similarities[i]) for i in vector_ids]
                if mode == "vector"
                else fuse(vector_ids, keyword_ids)
            )
            candidates = [
                Hit(
                    chunk=self.chunk_map[i],
                    score=float(score),
                    vector_rank=vector_ids.index(i) + 1 if i in vector_ids else None,
                    keyword_rank=keyword_ids.index(i) + 1 if i in keyword_ids else None,
                    initial_rank=rank,
                )
                for rank, (i, score) in enumerate(ranked[:16], 1)
            ]
            if mode == "reranked":
                scores = self.reranker.predict([(query, h.chunk.text) for h in candidates])
                for hit, score in zip(candidates, scores):
                    hit.rerank_score = float(score)
                selected = sorted(candidates, key=lambda h: h.rerank_score, reverse=True)
            else:
                selected = candidates
            return deduplicate(selected)[:top_k], candidates

    def close(self):
        if self.client:
            self.client.close()
