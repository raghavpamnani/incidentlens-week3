# Architecture and decisions

IncidentLens is a single-user localhost application. FastAPI serves a static responsive interface and typed API routes. Heavy model work runs in synchronous route handlers, not the ASGI event loop. A mutation lock serializes investigation with uploads; Qdrant local storage is deliberately single-process.

## Ingestion boundary

Adapters parse UTF-8 Markdown/text, validated CSV, and text PDFs. Docling preserves PDF tables and reading order in the full profile. OCR is disabled: scanned PDFs are not supported by this tested configuration. Each chunk retains document, section, parser, page and a deterministic content-derived ID. Long sections split near sentence boundaries with overlap. The implementation uses character budgets, not token-perfect table splitting; complex tables can still be split.

Known injection patterns quarantine entire chunks. Presidio sanitizes chunks before embedding, BM25 and graph extraction. Raw synthetic corpus files remain on disk but are never exposed through an HTTP source-download endpoint. Source inspection returns sanitized indexed passages.

Public fictional service/team terms are narrowly allowlisted for PERSON false positives. This does not exempt those spans from email, phone, card or secret detection. The allowlist is demo-domain configuration, not a general PII solution.

## Retrieval boundary

SentenceTransformer produces normalized local embeddings. Qdrant performs cosine retrieval; BM25 tokenization preserves exact error identifiers. Hybrid mode combines candidate ranks using RRF with k=60. CrossEncoder jointly scores the original query and candidate text. Sequence-based deduplication removes highly similar chunks. The inspector preserves each candidate's initial and per-retriever rank.

Up to sixteen candidates are reranked; four are returned by default. Chunk IDs never derive from model-generated citations. Index configuration prevents loading embeddings under a different model name. Corpus and dataset fingerprints accompany evaluation results.

## Graph boundary

The graph extracts only explicit domain sentences: `A depends on B.` and `A is owned by B.` It stores a source sentence, document and chunk ID on every edge. NetworkX bounds traversal to two hops. The graph is an evidence view, not an inferred incident root-cause engine. Entity co-occurrence alone creates no edge.

## Generation boundary

The local Transformers profile uses Qwen2.5-0.5B-Instruct in full setup (MPS when available, CPU otherwise); a 1.5B model is optional on machines with more memory. Ollama is a configurable alternative. Both generate typed JSON claims with citations. Pydantic validates the structure; cited IDs must belong to the retrieved context. Output passes through redaction and policy checks. Neither JSON validity nor citation existence guarantees faithfulness.

The separate `evidence` profile returns source excerpts and is labeled as extractive. It is not an automatic fallback for failed LLM answers. Generation failures return a visible status and still expose safe retrieved evidence.

Abstention requires overlap with the indexed domain and, in reranked mode, a positive best reranker score. This is a conservative heuristic evaluated on a small set, not a calibrated confidence model. Optional HyDE is generated locally, sanitized, used only as a vector query and never cited as evidence.

## Operational decisions

- No cloud API keys are required. First setup downloads public models; runtime can use their local cache.
- No arbitrary remote URL ingestion or operational command execution.
- No authentication: loopback binding is mandatory for this demo.
- Raw query contents are not logged by the application; Uvicorn access logs contain paths and status codes.
- Optional Llama Guard uses a local Ollama endpoint and fails closed on unavailable/invalid verdicts.
- Original bootcamp PDFs, CV, private files and credentials are outside this standalone repository.

Malformed JSON or claim structure receives at most one model formatting retry. Every resulting claim and citation is validated again; unknown citations fail immediately, and a second invalid response remains an explicit failure. The retry does not substitute canned answers.
