import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from incidentlens.config import settings
from incidentlens.pipeline import Pipeline

if __name__ == "__main__":
    p = Pipeline(settings)
    try:
        p.build()
        findings = [f.model_dump() for f in p.ingestion_findings]
        (settings.data_dir / "ingestion.json").write_text(json.dumps(findings, indent=2))
        print(f"Indexed {len(p.retriever.chunks)} chunks; {len(p.graph.edges)} relationships.")
        print("Guardrails:", findings)
    finally:
        p.retriever.close()
