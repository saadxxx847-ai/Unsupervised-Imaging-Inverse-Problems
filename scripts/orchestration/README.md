# Windows orchestration source copies

The original eight source files were copied without modification from group-pc:D:\DDM4IP-runtime\orchestration on 2026-09-17. The directory was refreshed on 2026-09-22 and now contains ten runtime source files. Original byte hashes are recorded in docs/publication/orchestration-manifest-20260917.json and docs/publication/orchestration-manifest-20260922.json.

The active deployment remains in that external runtime directory. Scripts keep their original host, repository, Python, cache, and runtime path checks. This directory is versioned source for preservation, not a new execution location or an instruction to launch a task.

- bdd100k_runner.py, run_bdd100k_stage.ps1, start_bdd100k_task.ps1, and step-spec.schema.json: existing real-unpaired route.
- run_bdd100k_synthetic_stage.ps1, start_bdd100k_synthetic_task.ps1, and synthetic-step-spec.schema.json: synthetic route; its Python runner is scripts/bdd100k_synthetic_runner.py.
- runner_fixture.py: no-training orchestration fixture, not a learned model or training artifact.
- step1_resume_watchdog.ps1: the guarded Step 1 recovery watchdog preserved for audit and reproducibility.
- watch_bdd100k_step2_full.ps1: a read-only terminal viewer for the five Step 2 full seed slots; Ctrl+C exits only the viewer.

Publication is authorized separately from execution. Follow AGENTS.md and the approved stage plan before any deployment, data processing, pilot, training, or evaluation.
