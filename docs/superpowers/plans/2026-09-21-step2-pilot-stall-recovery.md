# Step 2 Stalled Pilot Recovery and Anti-Recurrence Implementation Plan

> For agentic workers: use this plan task-by-task with test-first verification. Keep the existing stalled run immutable and use a new run root for every retry.

Goal: Eliminate the confirmed Windows Step 2 first-batch DataLoader hang, enforce the safe policy for future Step 2 runs, and rerun seed0 with observable progress and independently verifiable terminal checkpoints.

Architecture: The runner will fail closed against nonzero Step 2 DataLoader workers and will inject training.num_workers=0 when omitted. The retry spec will use one-process loading plus bounded report/save intervals so a healthy run emits progress and intermediate checkpoint evidence. The existing stalled run remains an immutable diagnostic record.

Tech Stack: Windows Task Scheduler, PowerShell 5.1, Python E:\Anaconda3\envs\ddm4ip\python.exe, Hydra, PyTorch 2.4.1+cu118, unittest, BDD100K synthetic benchmark runner.

Spec: docs/superpowers/specs/2026-09-06-bdd100k-known-blur-quantitative-reproduction-design.md

## Global Constraints

- Execute repository code, tests, probes, and training only on group-pc host DESKTOP-KBM1345.
- Preserve all existing dirty worktree changes and keep the old stalled run root immutable.
- Use D:\DDM4IP-runtime for all remote runtime, logs, probes, specs, checkpoints, and temporary files.
- Use a new external spec, new scheduled-task name, and new run root for the retry.
- Do not start Step 2 full, Step 3, formal evaluation, or any unrelated training.
- Step 2 must keep training.max_val_batches=0, an explicit verified Step 1 .pt predecessor, and no kernel_gt Hydra override.
- A terminal SUCCESS message is insufficient; independently verify scheduler, status/history, complete task log, command/spec, checkpoint hashes, internal steps 2048/2049, kernel_nn, and tensor finiteness.

---

### Task 1: Preserve and stop the stalled run

Files/artifacts:
- Preserve: D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step2-pilot-seed0-rerun-20260921
- Create: D:\DDM4IP-runtime\temp\step2-seed0-stall-audit-20260921

- [x] Record scheduler state, process command lines, GPU sample, log size/timestamp, and checkpoint inventory.
- [x] Stop the scheduled task, then terminate only the verified runner/training process tree.
- [x] Verify scheduler state is Ready and no matching project process remains.

### Task 2: Reproduce the first-batch failure boundary

Files/artifacts:
- Create: D:\DDM4IP-runtime\temp\step2-seed0-stall-audit-20260921\dataloader_probe.py
- Create: D:\DDM4IP-runtime\temp\step2-seed0-stall-audit-20260921\probe-4.json
- Create: D:\DDM4IP-runtime\temp\step2-seed0-stall-audit-20260921\probe-0.json

- [x] Compose exp=step2_bdd100k_synthetic with the frozen synthetic clean dataset and batch_size=32.
- [x] Call the same init_dataset and init_dataloader path used by DiffinstructOpTrainer.
- [x] Bound the first next(DataLoader) call to 90 seconds.
- [x] Verify num_workers=4 times out while num_workers=0 returns a 32 by 3 by 256 by 256 batch.

### Task 3: Add a failing runner policy regression

Files:
- Modify: scripts/bdd100k_synthetic_runner.py
- Test: tests/test_bdd100k_synthetic_runner.py

- [ ] Add a test proving a Step 2 command always contains exactly training.num_workers=0 when the field is omitted.
- [ ] Add a test proving an explicit nonzero Step 2 training.num_workers is rejected with a fail-closed error.
- [ ] Run only the new tests and record the expected RED failure before production changes.

### Task 4: Implement the single root-cause policy fix

Files:
- Modify: scripts/bdd100k_synthetic_runner.py

- [ ] In Step 2 validation, reject any explicit nonzero training.num_workers.
- [ ] In Step 2 override construction, inject training.num_workers=0 when it is absent.
- [ ] Do not change dataset contents, predecessor selection, kernel metadata, or checkpoint serialization in this task.
- [ ] Run the focused runner tests and verify GREEN.

### Task 5: Make the retry observable without changing its budget

Files:
- Create: D:\DDM4IP-runtime\experiments\phaseF-step2-pilot-spec-20260921-seed0-rerun2-20260921.json
- Create: D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step2-pilot-seed0-rerun2-20260921

- [ ] Copy only frozen benchmark hashes and verified Step 1 predecessor metadata.
- [ ] Keep training.batch_size=32, loss.n_accum_steps=1, training.max_steps=2048, and training.max_val_batches=0.
- [ ] Add training.num_workers=0, training.report_every_steps=128, and training.save_every_steps=512.
- [ ] Resolve Hydra config and assert no kernel_gt command injection.
- [ ] Verify target task and run root do not exist before launch.

### Task 6: Launch and perform one bounded existence check

- [ ] Launch only through start_bdd100k_synthetic_task.ps1.
- [ ] Verify scheduler Running, LastTaskResult=267009, runner/trainer process presence, status RUNNING, and task log growth.
- [ ] Stop waiting after this single check; do not continuously monitor the long task.

### Task 7: Independent terminal acceptance

- [ ] Parse every JSON object in status-history.jsonl by object boundary and require RESERVED -> RUNNING -> SUCCESS.
- [ ] Read the complete task.log and confirm no traceback or non-finite failure.
- [ ] Verify training-state-2048.pt SHA-256, internal global_step=2048, kernel_nn, and all tensors finite.
- [ ] Verify network-snapshot-2048.pkl SHA-256, internal global_step=2049, kernel_nn, and all tensors finite.
- [ ] Verify scheduler termination and LastTaskResult=0.
- [ ] Only after all gates pass may a future conversation request Step 2 full seeds 0–4.



### Task 8: rerun3 checkpoint-schema repair and independent terminal acceptance (2026-09-22)

- [x] Schema repair preflight passed remotely: focused checkpoint-schema suite 3/3, related no-training suite 35/35, full unittest discovery 80 tests, and Hydra resolve under the fixed project Python.
- [x] Only the new rerun3 external spec/run root/task was used. Budget remained batch_size=32, n_accum_steps=1, max_steps=2048, max_val_batches=0, report_every_steps=128, save_every_steps=512, num_workers=0, seed=0; no kernel_gt command/config override.
- [x] Independent terminal acceptance passed: scheduler Ready/LastTaskResult=0, no matching process, SUCCESS/0, complete RESERVED -> RUNNING -> SUCCESS history, complete log, exact flow_nn and kernel_nn in both endpoints, internal 2048/2049, all tensors/optimizer finite, no .tmp/.partial under the run root, and restored sys.path.
- [x] Classification: training completed and strict terminal acceptance PASS. Step 2 full, another seed, Step 3, and formal evaluation remain separately unauthorized.
