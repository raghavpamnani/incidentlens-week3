# Two-minute demo walkthrough

## Before recording

Run full setup, build the index, run evaluation with answers, then start the server. Open http://127.0.0.1:8030. Warm the model with one query. Check that the answer engine shows Local Qwen or Local Ollama, not evidence excerpts. Use a larger local Ollama model if available for stronger synthesis; rerun evaluations when switching it.

## 0:00–0:15 — Problem

“IncidentLens is a local investigation assistant for a fictional commerce platform. It brings evidence, dependency relationships and guardrails into one reviewable workflow. It cannot execute changes.”

## 0:15–0:45 — Investigation

Click Checkout timeout. Explain exact error-code matching and semantic retrieval. Open one answer citation. Show the source document, section and page when available. Note that INC-204 is historical evidence, not proof of a new root cause.

## 0:45–1:05 — Evidence and graph

Open the Evidence Inspector: vector rank, keyword rank, fused initial rank and reranker score. Show the related path Checkout Service → Payments API → Ledger Database / Payments Team. Click a relationship source to verify its sentence.

## 1:05–1:25 — Guardrails

Click Injection test; show the blocked status. Ask “What is our annual marketing budget?” and show insufficient evidence. In the library, explain that the corpus includes synthetic PII and a malicious fixture, sanitized or quarantined before indexing. Never display a real API key.

## 1:25–1:50 — Measured quality

Open Evaluation lab. Show real vector-only/hybrid/reranked results, the sixteen-question development set and individual failures. Explain that NLI faithfulness is an estimate and that the small corpus is not a production benchmark.

## 1:50–2:00 — Close

“Days 11–15 are visible in the pipeline: parsing, retrieval, reranking, relationships, evaluations and guardrails. The public repository includes modular code, setup instructions, tests and reproducible results.”

## Optional extended demo

Ask “What are the payment recovery verification thresholds?” to inspect the Docling PDF table and page citation. Show a HyDE-enabled query and disclose extra latency. Upload a new synthetic Markdown document through the library. Show generation failure honestly if the local model fails validation.
