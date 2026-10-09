# API contracts

Base URL: `http://127.0.0.1:8030`. OpenAPI UI: `/docs`.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/status` | Index, model profile and guardrail capabilities |
| POST | `/api/investigate` | Validate, sanitize, retrieve, generate and validate |
| GET | `/api/source/{chunk_id}` | Sanitized source passage and provenance |
| GET | `/api/graph` | Explicit relationships with source evidence |
| GET | `/api/documents` | Indexed document metadata |
| POST | `/api/upload` | Parse and index one local synthetic document |
| GET | `/api/evaluations` | Most recent saved benchmark report |

```bash
curl -s http://127.0.0.1:8030/api/investigate \
  -H 'Content-Type: application/json' \
  -d '{"query":"What does PAY-504 mean?","mode":"reranked","top_k":4,"hyde":false}'
```

`mode`: vector, hybrid or reranked. `top_k`: 1–8. HyDE requires a local LLM profile. Response includes status, sanitized query, answer claims with citations, selected hits, candidate ranks, graph evidence, guardrail findings, timings, generator and mode.

Statuses: answered, insufficient_evidence, blocked, generator_unavailable. Safety blocks are HTTP 200 with an explicit blocked status; clients must inspect the body. Malformed payloads: 422. Unsupported uploads: 415. Oversized uploads: 413. Existing document: 409. Unknown source: 404. Unavailable index: 503. Rate limit: 429. Cross-origin POST: 403.

Uploads rebuild the local index and may take time. This demo does not implement background jobs, authentication, raw-file serving or multi-user access.
