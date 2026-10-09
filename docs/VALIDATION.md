# Verified local run

Run timestamp: 2026-10-09T08:45:32.333241+00:00

Prepared generator: `Qwen/Qwen2.5-0.5B-Instruct` on the 8 GB local Mac.

- 39 automated tests passed; Ruff, JavaScript syntax and shell syntax checks passed.
- The dedicated Python environment has no broken dependencies.
- 7 synthetic documents, 21 indexed chunks, 10 source-backed graph relationships.
- 16 reviewed development questions; 11/11 targeted safety and answer-availability checks passed.
- All three final generated responses were available and cited only retrieved passages.

| Retrieval mode | Document precision | Document recall | MRR | Warm median latency |
| --- | ---: | ---: | ---: | ---: |
| vector | 0.573 | 0.927 | 1.000 | 35.5 ms |
| hybrid | 0.536 | 0.979 | 0.969 | 34.5 ms |
| reranked | 0.562 | 0.969 | 1.000 | 193.7 ms |

These are actual results on a small synthetic development set. Hybrid improved recall but did not improve every metric. Retrieval latency excludes model startup. See `EVALUATION.md` for methodology.

## Assistant review against source evidence

The PAY-504 answer gives the documented meaning and first metrics/traces to inspect. The INC-204 answer correctly identifies the connection leak, but omits the rollback and follow-up requested by the question; it is incomplete. The recovery answer gives the three numeric thresholds but omits the ten-minute verification window. The supporting runbook evidence remains available for review.

The NLI entailment estimates were 0.67, 1.00 and 0.67 respectively. Those estimates do not measure completeness. Valid citation membership does not establish semantic support or complete coverage of the question.

The historical-incident response needed one formatting retry. A second invalid output would still fail visibly; no canned answer is substituted.

The earlier 1.5B run is retained in `evaluation/larger-model-results.json`. It also omitted the historical rollback detail and placed more memory pressure on this machine. The prepared runtime uses 0.5B for practicality, without claiming that it achieves perfect answer quality.

Three model-generated evaluation candidates were schema-validated and assigned single-passage provenance. They remain marked as review-required and were not merged into the reviewed benchmark.

GitHub Actions is configured but has not run remotely. Public publication, recording the demo video, and assignment submission remain pending.

A live compound incident question initially produced an invented Payment Gateway API reference and an unsupported inventory-latency claim. The added name-consistency check rejects that response because the invented service is absent from its cited evidence. This is a narrow regression guard, not a complete hallucination detector. The walkthrough begins with the reviewed PAY-504 runbook question and uses the source-backed graph for ownership. Saved real-model answers were revalidated against this final name check without rerunning or relabeling their metrics.

The live compound question was repeated after adding the name check: its answer was withheld and the cited source passages remained available. The interface distinguishes a withheld response from a validated answer.

Final browser checks: the reviewed PAY-504 question returned a cited answer in 4.96 seconds; the same question with HyDE returned the same supported findings in 12.82 seconds. These are single observed end-to-end timings, not a latency benchmark. The citation dialog displayed the sanitized source passage.
