# Local handoff

The complete project lives in `Week 3/incidentlens`. It is a standalone Git repository, separate from the parent bootcamp checkout. No parent Git changes were staged or committed.

## Start the prepared demo

```bash
cd "Week 3/incidentlens"
bash scripts/start_demo.sh
```

Open http://127.0.0.1:8030. This start command forces model loading from the already downloaded local cache; run setup first on a new machine.

## Refresh evidence and results

Stop the server before opening embedded Qdrant from another process.

```bash
demo_python="$(cat .runtime-python)"
"$demo_python" scripts/build_index.py
"$demo_python" scripts/evaluate.py --with-answers
bash scripts/start_demo.sh
```

The prepared Python environment and active model cache are in `~/Library/Caches/incidentlens-week3`. The ignored `.runtime-python` file tells the start script which interpreter to use; `.env` supplies its model cache path. Original generated files remain ignored in the project.

`.runtime-python`, `.env`, `.venv`, `.models` and `data` are local-only and ignored by Git. The archive contains source, synthetic corpus, documentation and saved results; it does not include the environment or model cache.

## Pending external actions

The intended repository name is `raghavpamnani/incidentlens-week3`. Public publication requires user approval. No repository was created after automatic approval review rejected that action. The README clone URL is the intended destination for publication, not evidence that it already exists.

Record the two-minute video using `docs/DEMO_SCRIPT.md`, then submit the public repository and recording through the official bootcamp process. No video or assignment-form submission has been made.
