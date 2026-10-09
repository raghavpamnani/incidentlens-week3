#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
demo_python=.venv/bin/python
if [ -f .runtime-python ]; then
  read -r demo_python < .runtime-python
fi
if [ ! -x "$demo_python" ]; then
  printf 'Run bash scripts/setup.sh first.\n' >&2
  exit 1
fi
if [ ! -f data/chunks.json ]; then
  printf 'Build the index first: .venv/bin/python scripts/build_index.py\n' >&2
  exit 1
fi
printf 'IncidentLens: http://127.0.0.1:8030\n'
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
exec "$demo_python" -m uvicorn incidentlens.main:app --host 127.0.0.1 --port 8030
