"""Generate candidate synthetic Q&A; output is explicitly pending human review."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pydantic import BaseModel, Field

from incidentlens.config import ROOT, settings
from incidentlens.generation import Generator


class QA(BaseModel):
    question: str = Field(min_length=5, max_length=500)
    expected_answer: str = Field(min_length=5, max_length=1000)
    source_ids: list[str] = Field(min_length=1)


class Candidates(BaseModel):
    questions: list[QA] = Field(min_length=1, max_length=10)


if __name__ == "__main__":
    chunks = json.loads((settings.data_dir / "chunks.json").read_text())[:6]
    generator = Generator(settings)
    raw = generator._chat(
        [
            {
                "role": "system",
                "content": "Generate three test question-answer pairs from these source passages. "
                "Use only supported facts, include source_ids, return JSON with a questions array.",
            },
            {"role": "user", "content": json.dumps(chunks)},
        ],
        Candidates.model_json_schema(),
    )
    result = Candidates.model_validate_json(raw)
    allowed = {c["id"] for c in chunks}
    assert all(set(q.source_ids) <= allowed for q in result.questions), "Unknown source citation"
    (ROOT / "evaluation/candidates.json").write_text(
        json.dumps(
            {
                "review_required": True,
                "generator": settings.generator,
                "questions": result.model_dump()["questions"],
            },
            indent=2,
        )
    )
    print("Candidate dataset saved. Review factual support before adding it to questions.json.")
