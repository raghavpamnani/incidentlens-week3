#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -c 'import sys; assert (3,12) <= sys.version_info[:2] < (3,14), "Use Python 3.12 or 3.13"'
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev,pdf]'
.venv/bin/python -m spacy download en_core_web_sm
if [ ! -f .env ]; then
  cat > .env <<'CONFIG'
IL_GENERATOR=transformers
IL_LOCAL_LLM_MODEL=Qwen/Qwen2.5-0.5B-Instruct
IL_PII_NER=true
IL_PDF_PARSER=docling
CONFIG
fi
.venv/bin/python scripts/build_index.py
.venv/bin/python -c 'from incidentlens.config import settings; from incidentlens.generation import Generator; g=Generator(settings); g.load_local() if settings.generator == "transformers" else None'
printf '\nReady. Run: .venv/bin/uvicorn incidentlens.main:app --host 127.0.0.1 --port 8030\n'
