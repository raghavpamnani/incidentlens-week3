# Guardrail behavior and limitations

## Implemented controls

- Pydantic query length (3–2,000 characters), retrieval-mode enum and top-k bounds.
- Maximum 5 MB uploaded document; supported extensions; PDF signature check; sanitized basenames; duplicate-name rejection.
- Same-origin POST boundary and twenty writes per minute per client IP.
- Presidio email, phone, credit-card and API-key redaction; full profile adds spaCy PERSON NER.
- Redaction before embeddings, keyword indexing, graph extraction, generation and source display.
- Known direct/indirect injection patterns blocked or quarantined. The bundled malicious section is excluded from the index.
- Output JSON schema, allowed-source citation validation, redaction and policy checks.
- Self-hosted static assets, DOM textContent rendering, CSP, no-sniff and frame protections.
- Optional local Llama Guard classification. A configured classifier failure never permits the request.

## Limits

Regexes are not complete injection detection or semantic content moderation. The lightweight content policy matches a small set of harmful patterns; optional Llama Guard broadens classification but has not been verified in the saved default run. PII recognizers have false positives and negatives. API-key coverage is deliberately limited to configured patterns. This is not GDPR/HIPAA certification or a claim of guaranteed protection.

A generated answer with existing citations can still be unsupported. The NLI evaluator is an estimate; human review remains necessary. The small local generator is not suitable for autonomous operations.

The application is a localhost demo. Before deploying: add authentication and access controls, per-document permissions, isolated parsing workers, request/compute timeouts, robust resource quotas, dependency review, operational audit logs and stronger adversarial tests. Do not expose Uvicorn on 0.0.0.0.

Original uploaded files are stored locally, unsanitized; only indexed content is redacted. Use synthetic documents. The sample corpus intentionally includes fake test PII/secrets. Real private/client data must not be committed.

Malformed JSON or claim structure receives at most one model formatting retry. Every resulting claim and citation is validated again; unknown citations fail immediately, and a second invalid response remains an explicit failure. The retry does not substitute canned answers.

Capitalized API, Service, Database and Team references in generated claims must appear in the cited passages. This limited consistency check rejects invented names; it does not verify causal relationships or all possible entity spellings.
