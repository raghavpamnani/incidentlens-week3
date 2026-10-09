# Evaluation methodology

## Reviewed development set

`evaluation/questions.json` contains sixteen authored questions with document-level relevance labels reviewed against the fictional corpus. It covers exact identifiers, semantic retrieval, ownership, historical incidents and PDF thresholds. This is a small development set, not a representative unseen production benchmark. Parameters were developed against this domain; reported scores may overstate generalization.

## Retrieval ablations

Each configuration runs on the same index and questions: vector-only, hybrid RRF, hybrid plus cross-encoder. Four chunks are requested; selected documents are deduplicated before calculating document-level precision, recall and reciprocal rank. Consequently the values are not passage-level Ragas context precision/recall. Multiple relevant sections in one document count once. This is disclosed in the report and UI.

Models are warmed once per mode. Median query latency excludes setup and model loading. A single run is noisy; rigorous performance work needs repeated runs and p95/time-to-first-token measurements. This demo records end-to-end generation time rather than streamed time-to-first-token. No cloud token-cost comparison is claimed.

The report records dataset/corpus fingerprints, platform, Python version and selected model names. Run:

```bash
python scripts/evaluate.py
python scripts/evaluate.py --with-answers
```

Stop the server first, because embedded Qdrant can be opened by one process. Saved results are real run output, not live counters. Changes to uploads require a new evaluation run.

## Answers and faithfulness

With `--with-answers`, three questions receive actual local model answers. The evaluator checks cited-source membership and uses `cross-encoder/nli-MiniLM2-L6-H768` to estimate whether sentence-level claims are entailed by their cited context. The published label order is contradiction, entailment, neutral. The fraction classified as entailment is an estimate, not a correctness guarantee. Context truncation, domain language and multi-fact sentences can distort it. Results include individual statements and scores so failures can be reviewed.

Failed generation does not receive a perfect score: it has no claims, a null entailment rate, and a failed answer-availability check. Citation coverage alone is not faithfulness. No LLM judge is used to manufacture a high aggregate score.

`JudgeRubric` defines bounded numerical fields for optional future structured LLM judging. It is not an implemented judge in this run. Ragas and DeepEval are curriculum resources; neither is falsely claimed as executed here.

## Safety cases

The harness checks direct injection, secret requests, the limited content policy, absent-domain questions, synthetic PII/secrets, malicious-chunk exclusion and graph provenance. These are targeted smoke tests, not a comprehensive security certification.

## Synthetic candidates

`python scripts/generate_eval.py` uses the local LLM to create schema-validated candidate Q&A with source IDs. Output is explicitly pending review. Candidate answers must be checked against passages before merging into ground truth. The reviewed benchmark is kept independent of these candidates.
