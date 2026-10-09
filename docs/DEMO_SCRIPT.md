# IncidentLens video script — approximately 3 minutes

## Recording preparation

- Open http://127.0.0.1:8030/ and select Investigation.
- Select **Hybrid + reranking**, leave **HyDE off**, and click **Checkout timeout**.
- Run this query once before recording to warm the local model. Confirm a cited answer is visible. During recording, allow for actual model latency; the times below are pacing guides.
- Keep the repository open in a second tab: https://github.com/raghavpamnani/incidentlens-week3.
- Do not rebuild the index or rerun the evaluator while the server owns the embedded Qdrant database. Existing evaluation results are ready to show.
- Use only the supplied synthetic documents. If generation is withheld, explain the validation failure honestly and show retrieved evidence.

## 0:00–0:20 — Introduce the problem

**Screen:** Investigation home.

**Say:** “Hi, I’m Rahul Pamnani. This is IncidentLens, my Week 3 Core AI Engineering project. During an incident, useful information can be spread across runbooks, past incidents and service ownership records. IncidentLens brings these together as cited guidance using a fictional commerce platform. It runs locally and provides read-only investigation support.”

## 0:20–0:55 — Ask a question and verify the evidence

**Action:** Click Checkout timeout, with Hybrid + reranking selected and HyDE off. Click Investigate. Open an answer citation.

**Say:** “I’m asking: What does PAY-504 mean and what should we check first? The system retrieves relevant passages and gives them to the local language model. Each accepted claim links to retrieved evidence. I can open the citation and check its document and section. A past incident is supporting history; it does not establish the cause of a current outage.”

## 0:55–1:25 — Explain retrieval choices

**Action:** Show the retrieval dropdown, then open Evidence Inspector for the current result. Do not change the dropdown and describe the old result as a new run.

**Say:** “Vector only searches by meaning. Hybrid search combines that with keyword matching, which helps preserve exact identifiers such as PAY-504. Hybrid plus reranking adds a second model that reads the question and each candidate passage together, then reorders the passages by relevance. The inspector makes the vector rank, keyword rank and reranker score visible.”

## 1:25–1:45 — Explain HyDE

**Action:** Point to the HyDE checkbox; keep it off for the main recording.

**Say:** “HyDE stands for Hypothetical Document Embeddings. It asks the model to draft a hypothetical passage, then uses that passage to search for real documents. In this project, keyword search still uses the original question. The hypothetical text is a search aid, never a cited source. It adds another model call, and it is not guaranteed to improve every question.”

## 1:45–2:05 — Show the knowledge graph

**Action:** Open Knowledge map. Show Checkout Service, Payments API, Ledger Database and Payments Team. Open one relationship source.

**Say:** “The knowledge map shows explicit dependency and ownership relationships extracted from the documents. For example, I can follow Checkout Service to Payments API and inspect its dependencies and owner. Each relationship has source evidence. This graph complements the retrieval workflow.”

## 2:05–2:30 — Show safety behavior

**Action:** Return to Investigation. Click Injection test and submit. Then click Missing evidence and submit.

**Say:** “This instruction asks the assistant to ignore its rules and reveal its system prompt. The guardrail blocks it. This second question asks for a marketing budget that the corpus does not contain, so the system abstains. The ingestion pipeline also redacts supported PII and secret patterns and quarantines the known malicious fixture before indexing.”

## 2:30–2:50 — Show measured evaluation

**Action:** Open Evaluation lab and show the comparison table and individual cases.

**Say:** “I compare all three retrieval modes on the same sixteen-question development set. Precision measures how much retrieved material is relevant, recall measures how much expected evidence is found, and MRR measures how early the first relevant result appears. These are document-level results on a small synthetic corpus. The safety and answer checks are targeted checks; they do not prove perfect answers.”

## 2:50–3:10 — Close with implementation and limits

**Action:** Show the GitHub repository and successful Actions run.

**Say:** “The repository includes modular Python code, parsing and chunking, local Qdrant retrieval, reranking, source-backed graph relationships, evaluation results and guardrails. GitHub CI passes all thirty-nine tests. The small local model can still omit details, so users should review the sources. IncidentLens demonstrates an inspectable AI engineering workflow from documents to evidence-backed guidance.”

## Optional extra clip — actual HyDE comparison

Run the same question with HyDE off, inspect evidence, then turn HyDE on and submit again. Compare the new retrieved passages and measured latency. Say: “This demonstrates how the retrieval changes for this question. I have not established that HyDE improves the whole benchmark.” Do not promise a better result or a fixed response time.

# Presenter notes: retrieval and HyDE

Retrieval means finding relevant passages before the language model writes an answer. Retrieval chooses the evidence; generation writes from that evidence. Changing a retrieval option does not switch the answer model.

| UI choice | What it does in IncidentLens | Main tradeoff |
| --- | --- | --- |
| Vector only | Embeds the query and searches Qdrant for passages with similar meaning | Can find paraphrases; exact identifiers can be less reliable |
| Hybrid search | Combines vector search and BM25 keyword rankings using reciprocal rank fusion | Balances meaning and exact terms; a combined rank is not a probability |
| Hybrid + reranking | Reorders hybrid candidates with a cross-encoder before selecting context | Adds relevance assessment and processing time; not guaranteed to win on every metric |
| HyDE checkbox | Generates a hypothetical passage for the vector search while retaining the original question for keywords and reranking | Extra generation latency; a misleading hypothetical passage can steer retrieval poorly |

An embedding is a numerical representation of text used to compare meaning. BM25 ranks passages using matching terms and their rarity. A cross-encoder jointly reads a question and passage to score relevance. The reranker score is not a confidence percentage.

HyDE example (illustrative, not evidence): the question “Why might checkout be timing out?” could produce a hypothetical passage mentioning payment dependency latency and database connection pools. That passage helps locate similar real runbooks. The final answer must cite actual retrieved documents, never that imagined passage.

For this recording, use Hybrid + reranking with HyDE off as the main path. Use Evaluation lab to discuss measured differences; a single live answer is not a benchmark. Avoid calling the project production-ready or claiming citation membership proves every claim is true.

HyDE reference: Gao et al., ACL 2023, [Precise Zero-Shot Dense Retrieval without Relevance Labels](https://aclanthology.org/2023.acl-long.99/).
