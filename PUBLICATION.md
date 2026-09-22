# BDD100K project source publication

This repository preserves the upstream [DDM4IP](https://github.com/inria-thoth/ddm4ip) history and MIT license, plus the BDD100K work developed on group-pc (DESKTOP-KBM1345). The upstream base is commit 7804d029aeb66ba6e2b20db00ff846ff3d6403cf.

## Publication scope — 2026-09-17

The owner authorized publication of complete project source and documentation to saadxxx847-ai/Unsupervised-Imaging-Inverse-Problems. Included are source, Hydra configurations, tests, notebooks, the original README illustration, approved designs, implementation plans, WORKLOG, and source copies of the Windows orchestration scripts.

Datasets, generated benchmark pixels, pretrained weights, training checkpoints, experiment outputs, caches, environment installations, credentials, and raw runtime logs are excluded. Historical facts and artifact hashes recorded in WORKLOG remain included. This source publication is not a backup of training artifacts.

[Source manifest](docs/publication/source-manifest-20260917.json) records the original 197 remote working-tree files before publication documentation was added. [Orchestration manifest](docs/publication/orchestration-manifest-20260917.json) records eight runtime source files. These SHA-256 values describe original file bytes; Git text line-ending conversion can change checkout byte hashes without changing text content.

## Project entry points

- [Approved synthetic design](docs/superpowers/specs/2026-09-06-bdd100k-known-blur-quantitative-reproduction-design.md)
- [Original implementation plan](docs/superpowers/plans/2026-09-06-bdd100k-known-blur-quantitative-reproduction.md)
- [Remediation and continuation plan](docs/superpowers/plans/2026-09-08-bdd100k-task10-remediation-and-continuation.md)
- [b16 formal fallback amendment](docs/superpowers/specs/2026-09-10-task11-step1-b16-formal-fallback-amendment.md)
- [b16 formal fallback plan](docs/superpowers/plans/2026-09-10-task11-step1-b16-formal-fallback.md)
- [Project work log](WORKLOG.md)

Read WORKLOG in full: historical entries were both prepended and appended, so the top of the file is not a complete current-state summary. Earlier plan checkboxes are historical and do not override later acceptance records or amendments.

The synthetic experiment uses 1,739 clean source images split into 1,000 Step 1 observations, 100 independent Step 2 clean images, 500 paired test images, and 139 development images. It reproduces a known-degradation protocol in the BDD100K domain, not the paper's original FFHQ numerical results. The separate real-unpaired BDD100K route retains its no-reference metric boundary.

The recorded Step 1 formal b16 contract is Scheme A: batch 16, accumulation 8, effective global batch 128, max_steps 5,242,880, and 40,960 optimizer updates. This publication does not restart training or certify the terminal checkpoint. A 2026-09-17 read-only scheduler snapshot returned Ready / LastTaskResult 0; full independent terminal acceptance is still required before downstream use.

## Execution environment

The existing project environment is remote Windows with Python at E:\Anaconda3\envs\ddm4ip\python.exe, PyTorch 2.4.1+cu118, and DeepInv 0.4.2. Project caches, data, logs, and checkpoints live under D:\DDM4IP-runtime. Existing configurations and wrappers contain host-specific paths and guards; cloning this repository alone does not provision those resources.

From the repository root, the actual module entry point is `python -m ddm4ip.main`. The upstream README retains its original examples; bare `python main.py` is not the root entry point. Runtime environment variables and the separately authorized Scheduled Task workflow remain required for experiments. Do not start training simply to verify this upload.

scripts/orchestration/ contains versioned source copies of previously external runtime files. This publication adds those copies for completeness; it does not relocate or modify active scripts under D:\DDM4IP-runtime\orchestration, register tasks, or change the approved training protocol. Consult existing plans before any installation or execution; do not overwrite an active runtime script without comparing its hash and preserving the existing version.

Future project development and tests remain on the verified remote host. Git commits and pushes for this publication are performed only from the owner's personal computer; no GitHub credentials are installed on the shared computer.

## Source update — 2026-09-22

The publication was refreshed from the current working tree on group-pc after the Step 1 formal run and Step 2 pilot/recovery work. The update contains source code, tests, configurations, plans, and project documentation only. It does not contain datasets, generated benchmark pixels, pretrained weights, training checkpoints, experiment outputs, caches, raw runtime logs, or credentials.

[Source manifest (2026-09-22)](docs/publication/source-manifest-20260922.json) records 202 remote working-tree files. Two local `.orig` backup files were intentionally excluded. The published `readme.md` retains its three-line pointer to this publication note, so that one file intentionally differs from the raw remote-source manifest. [Orchestration manifest (2026-09-22)](docs/publication/orchestration-manifest-20260922.json) records ten external runtime source files. The new source includes checkpoint validation and recovery tests, the Step 2 stall-recovery plan, the Step 1 resume watchdog, and the read-only Step 2 full progress viewer.

At the time of this source freeze, only Task 12 Step 2 full `seed0` had been launched. Its terminal result had not yet been accepted. Publishing this source does not stop, restart, validate, or advance that training run, and it does not authorize `seed1`–`seed4`, Step 3, formal evaluation, or data processing.
