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

The project was published with explicit owner approval to https://github.com/raghavpamnani/incidentlens-week3. Both `main` and `codex/incidentlens-foundation` preserve the implementation history.

Record the two-minute video using `docs/DEMO_SCRIPT.md`, then submit the public repository and recording through the official bootcamp process. No video or assignment-form submission has been made.

## Local Git storage

Git metadata is kept in `~/Library/Application Support/IncidentLens/git`, reached through the standard `.git` gitdir pointer in this folder. This avoids the Documents-folder mmap timeouts encountered during finalization. Original metadata is preserved under ignored `data/git-metadata-backup`. All recovered objects were hash-verified and `git fsck --full` completed successfully.

`main` and `codex/incidentlens-foundation` preserve the genuine implementation commits. A separate `IncidentLens-history.bundle` is supplied beside the source archive for a portable history backup. To clone that bundle, run `git clone IncidentLens-history.bundle incidentlens-restored` and then follow the README setup instructions. The source ZIP excludes runtime files and Git metadata.
