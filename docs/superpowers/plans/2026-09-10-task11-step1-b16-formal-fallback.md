# Task 11 Step 1 b16 Formal Fallback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run only the formally authorized Task 11 Step 1 training with `batch_size=16`, preserving the synthetic benchmark protocol and documenting the deviation from the original b32 full-training contract.

**Architecture:** Keep the parent design and accepted b32 pilot immutable. Freeze a new b16 external spec and run root, launch it through the existing Windows Scheduled Task runner, and independently validate the terminal artifacts before any downstream stage.

**Tech Stack:** Windows PowerShell 5.1, `group-pc` / `DESKTOP-KBM1345`, `E:\Anaconda3\envs\ddm4ip\python.exe`, Hydra, PyTorch, Windows Task Scheduler, SHA-256, and the existing synthetic runner.

**Spec:** `docs/superpowers/specs/2026-09-10-task11-step1-b16-formal-fallback-amendment.md`, together with the parent design `docs/superpowers/specs/2026-09-06-bdd100k-known-blur-quantitative-reproduction-design.md`.

## Current decision status (2026-09-10)

- On 2026-09-10 the user explicitly selected A, so the b16 formal budget is now frozen as sample/global-step preserving: `max_steps=5242880`, effective global batch `128`, and `40960` optimizer updates.
- The unselected alternative B remains optimizer-update preserving at `max_steps=2621440`, `20480` optimizer updates, and `50%` of the parent sample budget; it must not be substituted into the A spec and would require a new explicit amendment if selected later.
- This budget selection does not authorize external-spec creation, `prepare`, Scheduled Task registration, `execute`, or training. The b32 pilot and b16 pilot remain immutable reference evidence; the b16 formal run must use a new spec and run root after separate execution authorization.

## Global Constraints

- Execute repository commands only on `group-pc`; verify `hostname=DESKTOP-KBM1345` before each stage.
- Do not modify or overwrite the accepted b32 run root, b16 pilot run root, benchmark data, or prior checkpoint evidence.
- The external spec must be frozen under `D:\DDM4IP-runtime\experiments` and executed only through the Scheduled Task path; `direct` execution is forbidden.
- Freeze the budget basis before launch: sample/global-step preserving means `max_steps=5242880` and 40960 b16 optimizer updates; optimizer-update preserving means `max_steps=2621440` and half the parent sample budget. `max_steps=8192` is pilot-only.
- Step 1 execution requires a separate explicit user authorization; this plan and the documentation amendment do not launch training.
- Step 2, Step 3, formal evaluation, weight downloads, and data processing require separate later authorization.
- No Git commit, push, pull, branch change, or credential operation is part of this plan.

---

### Task 1: Freeze the b16 formal budget and external spec

**Files:**
- Create: `D:\DDM4IP-runtime\experiments\<new-b16-full-spec>.json`
- Reference: `docs/superpowers/specs/2026-09-10-task11-step1-b16-formal-fallback-amendment.md`

**Interfaces:**
- Consumes: accepted benchmark root, source manifest hashes, parent Phase E full-training contract, and accepted b16/b32 pilot evidence.
- Produces: one new external spec with `stage=step1`, `mode=full`, `training.batch_size=16`, explicit `max_steps`, expected global step, expected optimizer updates, and a unique new run root.

- [ ] **Step 1: Select and record the budget basis.** Use the sample/global-step-preserving option for a scientifically comparable full fallback unless the user explicitly selects the optimizer-update-preserving budget-reduced option. Do not use the pilot budget.
- [ ] **Step 2: Validate the spec fields.** Confirm host, Python, benchmark root, source/pairs/kernel hashes, `stage`, `mode`, unique run root, `batch_size`, `n_accum_steps=8`, `max_steps`, and derived update count.
- [ ] **Step 3: Confirm no existing target.** Reject any pre-existing spec or run root instead of overwriting it.

### Task 2: Perform read-only preflight

**Files:**
- Read: the new external spec, benchmark manifests, accepted b16 pilot checkpoint, and remote repository status.
- Create at runtime: the reserved spec and run root only through the existing prepare workflow.

**Interfaces:**
- Consumes: the frozen external spec from Task 1.
- Produces: a reserved run root with a copied `spec.json`, recorded runner hash, and no training process.

- [ ] **Step 1: Re-verify host and worktree.** Run `hostname`, `git status --short`, and verify the existing dirty worktree is unchanged.
- [ ] **Step 2: Re-verify b16 pilot provenance.** Check the pilot status, final checkpoint pair, SHA-256, internal global step, exact `flow_nn` keys, and tensor finiteness without modifying the pilot.
- [ ] **Step 3: Run prepare only.** Confirm the reserved spec preserves the chosen budget and that no project Python training module was executed.

### Task 3: Launch the b16 formal run through Scheduled Task

**Files:**
- Create at runtime: one new `DDM4IP-BDD100K-SYNTH-Step1-Full-b16` task and its dedicated run root.

**Interfaces:**
- Consumes: the prepared run-root `spec.json` from Task 2.
- Produces: a Scheduled Task, `RUNNING` status, append-only task log, and training outputs under the new run root.

- [ ] **Step 1: Obtain separate execution authorization.** Do not infer it from approval of this document amendment.
- [ ] **Step 2: Start the task with the existing `start_bdd100k_synthetic_task.ps1` workflow.** Pass the prepared run-root spec, never the external spec directly to execute.
- [ ] **Step 3: Perform one post-dispatch check.** Confirm task existence, matching process, `RUNNING` status, updated log, and run-root config; then stop polling and provide the user’s status/log commands.

### Task 4: Independently accept the terminal b16 checkpoint

**Files:**
- Read: status files, full task log, resolved Hydra files, `training-state-*.pt`, `network-snapshot-*.pkl`.

**Interfaces:**
- Consumes: the completed b16 formal run root.
- Produces: an acceptance record with terminal task result, status-history object count, checkpoint hashes, internal N/N+1 steps, model-key equality, and full tensor-finiteness result.

- [ ] **Step 1: Verify task and status evidence.** Require `Ready`, `LastTaskResult=0`, `status=SUCCESS`, exit code 0, matching process exit, and complete `RESERVED → RUNNING → SUCCESS` history.
- [ ] **Step 2: Verify checkpoint provenance.** Hash both final files and confirm the expected filenames, internal steps, and exact `flow_nn` state-dict keys.
- [ ] **Step 3: Verify numerical integrity.** Load both artifacts read-only and require all scanned tensors to be finite.
- [ ] **Step 4: Record the result.** Append only independently verified facts to the remote `WORKLOG.md`; do not upgrade b32 into the b16 result or authorize downstream stages.

### Task 5: Gate downstream stages

**Files:**
- Read: the accepted b16 formal checkpoint and the parent Step 2/3 specs.

**Interfaces:**
- Consumes: the independently accepted b16 formal checkpoint from Task 4.
- Produces: no execution unless the user opens a separate Step 2 authorization stage.

- [ ] **Step 1: Keep Step 2 and Step 3 stopped.** Do not inject the b16 checkpoint into downstream specs automatically.
- [ ] **Step 2: If later authorized, record the b16 provenance.** Include the exact checkpoint path, SHA-256, internal global step, and model-key validation in the downstream external spec.
