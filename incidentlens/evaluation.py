"""Reproducible retrieval metrics and model-assisted entailment estimates."""

import re

from pydantic import BaseModel, Field

from incidentlens.models import AnswerClaim, Chunk


class JudgeRubric(BaseModel):
    faithfulness: int = Field(ge=1, le=5)
    completeness: int = Field(ge=1, le=5)
    relevance: int = Field(ge=1, le=5)
    rationale: str = Field(max_length=1000)


def retrieval_metrics(documents: list[str], relevant: list[str]) -> dict[str, float]:
    unique = list(dict.fromkeys(documents))
    truth = set(relevant)
    found = sum(doc in truth for doc in unique)
    first = next((i for i, doc in enumerate(unique, 1) if doc in truth), None)
    return {
        "precision": found / len(unique) if unique else 0,
        "recall": found / len(truth) if truth else 0,
        "mrr": 1 / first if first else 0,
    }


class FaithfulnessEstimator:
    def __init__(self, cache_dir: str):
        from sentence_transformers import CrossEncoder

        self.model = CrossEncoder(
            "cross-encoder/nli-MiniLM2-L6-H768",
            device="cpu",
            cache_folder=cache_dir,
            max_length=512,
        )

    def score(self, claims: list[AnswerClaim], chunks: dict[str, Chunk]) -> dict:
        pairs = []
        statements = []
        for claim in claims:
            premise = "\n".join(chunks[i].text for i in claim.citations if i in chunks)
            for statement in re.split(r"(?<=[.!?])\s+", claim.text):
                if statement.strip():
                    pairs.append((premise, statement))
                    statements.append(statement)
        if not pairs:
            return {
                "entailment_rate": None,
                "statements": [],
                "note": "No answer claims to assess.",
            }
        scores = self.model.predict(pairs, apply_softmax=True)
        labels = ["contradiction", "entailment", "neutral"]
        entries = [
            {"text": text, "label": labels[int(s.argmax())], "entailment_probability": float(s[1])}
            for text, s in zip(statements, scores)
        ]
        return {
            "entailment_rate": sum(e["label"] == "entailment" for e in entries) / len(entries),
            "statements": entries,
            "note": "NLI estimate, not a guarantee. Domain language and truncation can mislead it.",
        }
