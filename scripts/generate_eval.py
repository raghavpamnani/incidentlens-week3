"""Generate candidate synthetic Q&A; output is explicitly pending human review."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pydantic import BaseModel, Field

from incidentlens.config import ROOT, settings
from incidentlens.generation import Generator


class QAContent(BaseModel):
    question: str = Field(min_length=5, max_length=500)
    expected_answer: str = Field(min_length=5, max_length=1000)


class QA(QAContent):
    source_ids: list[str] = Field(min_length=1)


class Candidates(BaseModel):
    questions: list[QA] = Field(min_length=1, max_length=10)


if __name__ == "__main__":
    chunks = json.loads((settings.data_dir / "chunks.json").read_text())
    selected = list({c["document"]: c for c in reversed(chunks)}.values())[:3]
    generator = Generator(settings)
    questions = []
    for chunk in selected:
        raw = generator._chat(
            [
                {
                    "role": "system",
                    "content": "Generate one test question and answer from this single passage. "
                    "Use only supported facts. Return exactly a JSON object with question and "
                    "expected_answer string fields, no Markdown.",
                },
                {"role": "user", "content": chunk["text"]},
            ],
            QAContent.model_json_schema(),
        )
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        content = QAContent.model_validate_json(raw)
        # Provenance is assigned from the single supplied passage, never invented by the LLM.
        questions.append(QA(**content.model_dump(), source_ids=[chunk["id"]]))
    result = Candidates(questions=questions)
    allowed = {c["id"] for c in chunks}
    if not all(set(q.source_ids) <= allowed for q in result.questions):
        raise ValueError("Unknown source citation")
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
