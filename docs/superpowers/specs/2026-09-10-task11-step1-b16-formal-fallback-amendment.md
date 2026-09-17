# Task 11 Step 1 Formal b16 Fallback Amendment

**Status:** Decision recorded on 2026-09-10; documentation only. No formal training was started by this amendment.

**Parent design:** `docs/superpowers/specs/2026-09-06-bdd100k-known-blur-quantitative-reproduction-design.md`

## Decision

The b32 Step 1 pilot completed naturally and passed independent terminal acceptance, but required approximately 3 hours 53 minutes. The accepted b16 pilot completed the same 64 optimizer updates in approximately 8 minutes 28 seconds. Because the reporting deadline is near, the formal Task 11 Step 1 route is amended to use `batch_size=16` as a documented fallback.

This is a protocol deviation and fallback, not a claim that b16 and b32 are numerically equivalent. Batch size changes gradient statistics, optimization trajectory, and the resulting checkpoint.

## Scope and invariants

- This amendment applies only to Task 11 Step 1 formal training for the synthetic known-motion-blur benchmark.
- The synthetic source manifest, role split, fixed degradation, model architecture, loss, seed, `n_accum_steps`, validation boundary, and metric boundaries remain those of the parent design.
- The accepted b32 pilot remains an immutable scale/performance reference. Its run root and checkpoint pair must not be overwritten or used as the b16 formal result.
- Step 2, Step 3, and formal evaluation remain separate stages and require separate user authorization.

## b16 formal configuration contract

- The formal external spec must set `training.batch_size=16` and use a new run root under `D:\DDM4IP-runtime\experiments`.
- With one rank and `loss.n_accum_steps=8`, the effective b16 global batch is 128.
- The parent Phase E full-training contract records `batch_size=32`, `n_accum_steps=8`, `max_steps=5242880`, `report_every_steps=16384`, `plot_every_steps=131072`, and `save_every_steps=2097152`. The b16 amendment must explicitly choose and record one budget basis before execution:
  - **Sample/global-step preserving:** keep `max_steps=5242880`; b16 then performs `5242880/128=40960` optimizer updates. This is the scientifically comparable full-budget fallback, but the b16 pilot rate extrapolates to roughly 90 hours; that estimate is planning evidence, not a guarantee.
  - **Optimizer-update preserving:** use `20480` updates, which derives `max_steps=20480*128=2621440`; this uses half the parent global-step/sample budget and must be reported as a budget-reduced b16 fallback, not as an equivalent full-budget run.
  - `max_steps=8192` remains the accepted b16 pilot budget (64 updates), not a formal full run.
- The new run must be launched only through the Windows Scheduled Task path after explicit execution authorization. `prepare` may freeze and validate the spec, but must not execute project training.
- Final acceptance must independently verify task state and exit code, status history by JSON-object boundaries, full task log, resolved configuration, final checkpoint SHA-256, internal global step, exact `flow_nn` keys, and tensor finiteness.

## Reporting language

Report the result as: “Task 11 Step 1 formal training with the documented b16 fallback,” including the selected budget basis. Do not report it as an equivalent b32 run or as direct reproduction of a b32 configuration. The b32 pilot may be reported separately as an accepted but unusually slow scale pilot.
