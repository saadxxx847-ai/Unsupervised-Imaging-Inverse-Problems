# Windows orchestration source copies

These eight source files were copied without modification from group-pc:D:\DDM4IP-runtime\orchestration on 2026-09-17. Their original byte hashes are recorded in docs/publication/orchestration-manifest-20260917.json.

The active deployment remains in that external runtime directory. Scripts keep their original host, repository, Python, cache, and runtime path checks. This directory is versioned source for preservation, not a new execution location or an instruction to launch a task.

- bdd100k_runner.py, run_bdd100k_stage.ps1, start_bdd100k_task.ps1, and step-spec.schema.json: existing real-unpaired route.
- run_bdd100k_synthetic_stage.ps1, start_bdd100k_synthetic_task.ps1, and synthetic-step-spec.schema.json: synthetic route; its Python runner is scripts/bdd100k_synthetic_runner.py.
- runner_fixture.py: no-training orchestration fixture, not a learned model or training artifact.

Publication is authorized separately from execution. Follow AGENTS.md and the approved stage plan before any deployment, data processing, pilot, training, or evaluation.
