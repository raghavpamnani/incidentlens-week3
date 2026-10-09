#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
demo_python=.venv/bin/python
if [ -f .runtime-python ]; then
  read -r demo_python < .runtime-python
else
  python3 -m venv .venv
fi
"$demo_python" -c 'import sys; assert (3,12) <= sys.version_info[:2] < (3,14), "Use Python 3.12 or 3.13"'
"$demo_python" -m pip install -r requirements.lock
"$demo_python" -m pip install --no-deps -e .
"$demo_python" -c 'import spacy; assert spacy.util.is_package("en_core_web_sm"), "NER model missing from lock install"'
if [ ! -f .env ]; then
  cat > .env <<'CONFIG'
IL_GENERATOR=transformers
IL_LOCAL_LLM_MODEL=Qwen/Qwen2.5-0.5B-Instruct
IL_PII_NER=true
IL_PDF_PARSER=docling
CONFIG
fi
"$demo_python" scripts/build_index.py
"$demo_python" -c 'from incidentlens.config import settings; from incidentlens.generation import Generator; g=Generator(settings); g.load_local() if settings.generator == "transformers" else None'
printf '\nReady. Run: bash scripts/start_demo.sh\n'
