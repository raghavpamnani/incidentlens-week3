from time import perf_counter

import httpx

from incidentlens.config import Settings
from incidentlens.generation import Generator
from incidentlens.graph import KnowledgeGraph
from incidentlens.guardrails import Guardrails
from incidentlens.models import Finding, Investigation, SearchRequest
from incidentlens.parsing import chunk_pages, read_pages
from incidentlens.retrieval import Retriever, tokens


class Pipeline:
    def __init__(self, cfg: Settings):
        self.cfg = cfg
        self.guard = Guardrails(cfg)
        self.retriever = Retriever(cfg)
        self.generator = Generator(cfg)
        self.graph = KnowledgeGraph([])
        self.ingestion_findings: list[Finding] = []

    def build(self):
        self.ingestion_findings = []
        safe = []
        for path in sorted(self.cfg.corpus_dir.iterdir()):
            if path.suffix.lower() not in {".md", ".txt", ".csv", ".pdf"}:
                continue
            for chunk in chunk_pages(path, read_pages(path, self.cfg.pdf_parser)):
                reason = self.guard.blocked(chunk.text)
                if reason:
                    self.ingestion_findings.append(Finding(kind=reason, action="quarantined"))
                    continue
                chunk.text, findings = self.guard.redact(chunk.text)
                self.ingestion_findings.extend(findings)
                safe.append(chunk)
        self.graph = KnowledgeGraph(safe)
        self.retriever.index(safe)

    def load(self):
        self.retriever.load()
        self.graph = KnowledgeGraph(self.retriever.chunks)

    def investigate(self, request: SearchRequest) -> Investigation:
        started = perf_counter()
        clean, findings = self.guard.redact(request.query)
        result = Investigation(
            query=clean,
            status="insufficient_evidence",
            answer="",
            guardrails=findings,
            generator=self.cfg.generator,
            mode=request.mode,
        )
        reason = self.guard.blocked(request.query)
        if reason or not self.guard.classify(clean):
            result.status = "blocked"
            result.answer = "This request was blocked by the configured safety policy."
            result.guardrails.append(Finding(kind=reason or "safety_classifier", action="blocked"))
            result.timings_ms["total"] = round((perf_counter() - started) * 1000, 2)
            return result
        t = perf_counter()
        vector_query = None
        if request.hyde:
            vector_query = self.generator.hyde(clean)
            vector_query, extra = self.guard.redact(vector_query)
            if self.guard.blocked(vector_query):
                raise ValueError("HyDE output failed the prompt-injection policy")
            result.guardrails.extend(extra)
            result.hyde_used = True
        result.timings_ms["hyde"] = round((perf_counter() - t) * 1000, 2)
        t = perf_counter()
        result.hits, result.candidates = self.retriever.search(
            clean, request.mode, request.top_k, vector_query
        )
        result.timings_ms["retrieval_and_reranking"] = round((perf_counter() - t) * 1000, 2)
        result.graph = self.graph.related(clean)
        # Conservative abstention: require named domain overlap and positive reranker evidence.
        domain_tokens = set(tokens(" ".join(self.graph.graph.nodes))) | {
            "pay-504",
            "inv-409",
            "auth-401",
            "inc-204",
            "pool",
            "rollback",
            "token",
        }
        domain_match = bool(set(tokens(clean)) & domain_tokens)
        supported = bool(result.hits) and domain_match
        if request.mode == "reranked" and result.hits:
            supported = supported and result.hits[0].rerank_score > 0
        if not supported:
            result.answer = (
                "The indexed documents do not provide enough evidence to answer this question."
            )
        else:
            t = perf_counter()
            try:
                generated = self.generator.answer(clean, result.hits)
                for claim in generated.claims:
                    claim.text, extra = self.guard.redact(claim.text)
                    result.guardrails.extend(extra)
                    if self.guard.blocked(claim.text) or not self.guard.classify(claim.text):
                        raise ValueError("Generated output failed safety policy")
                result.claims = generated.claims
                result.status = "answered" if generated.claims else "insufficient_evidence"
                result.answer = "\n\n".join(c.text for c in generated.claims) or (
                    "The retrieved evidence does not support an answer."
                )
            except (ValueError, RuntimeError, OSError, httpx.HTTPError) as exc:
                result.status = "generator_unavailable"
                result.answer = (
                    "Generation failed validation or is unavailable. Inspect the evidence below."
                )
                result.guardrails.append(
                    Finding(kind=type(exc).__name__, action="generation_failed")
                )
            result.timings_ms["generation"] = round((perf_counter() - t) * 1000, 2)
        result.timings_ms["total"] = round((perf_counter() - started) * 1000, 2)
        return result
