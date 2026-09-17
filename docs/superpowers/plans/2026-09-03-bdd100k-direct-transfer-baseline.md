# BDD100K Direct-Transfer Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** 在 group-pc 上完成一次可追溯的 BDD100K 三阶段直接迁移基线；三阶段各占一个可在任意时段启动的独立计划任务，并只用无参考证据定位主要失败模式。

**Architecture:** 先生成确定性的 Q2/Q3 硬链接数据视图；以测试驱动方式补齐 Step 3 的 noisy-only 数据接口与重投影残差；再加入 BDD100K Hydra 配置和计划任务运行器。pilot 仅用于测时和验证，完整阶段只能在前一阶段产物被独立核验后启动。

**Tech Stack:** Python 3.10 at E:\Anaconda3\envs\ddm4ip\python.exe; PyTorch 2.4.1+cu118; Hydra; DeepInv; Windows PowerShell 5.1; Windows Task Scheduler; unittest; NTFS hard links.

## Global Constraints

- 所有仓库读取、编辑、测试、训练和数据处理只在 hostname 为 DESKTOP-KBM1345 的 group-pc 上进行。
- 只能只读检查 Git。不得 add、commit、push、pull、rebase、切换分支或配置凭据。
- 保留所有既有修改；已有视图、输出根、检查点和计划任务一律拒绝覆盖。
- 项目入口固定为 E:\Anaconda3\envs\ddm4ip\python.exe -m ddm4ip.main。
- 每个项目 Python 进程仅设置进程级 TEMP、TMP、PIP_CACHE_DIR、TORCH_HOME 和 XDG_CACHE_HOME 到 D:\DDM4IP-runtime。
- Step 2 固定 training.max_val_batches=0。Step 3 固定 Batch.clean=None，且不得报告相对于 clean 图的 PSNR、SSIM、LPIPS。
- 所有耗时任务由 Windows 计划任务托管。启动后只确认一次任务、进程、状态和日志；随后由用户查看。
- 完整根目录：D:\DDM4IP-runtime\experiments\bdd100k-direct-transfer-20260903；pilot 根目录为同名加 -pilot。

---

### Task 1: 验证并创建 Q2/Q3 硬链接数据视图

**Files:**
- Read/Test: scripts\build_bdd100k_views.py and tests\test_bdd100k_view_builder.py
- Create at runtime: D:\DDM4IP-runtime\group-data-views\BDD100K_Blur_Sharp\

**Consumes:** Source data at D:\DDM4IP-runtime\group-data\BDD100K_Blur_Sharp and audit CSV at D:\DDM4IP-runtime\data-audit\bdd100k_proxy_metrics_20260902.csv.

**Produces:** train/clean, train/noisy, val/clean, val/noisy, manifest.csv and summary.json.

- [x] **Step 1: Check host, source inputs and target absence**

~~~powershell
hostname
Set-Location -LiteralPath 'D:\Unsupervised Imaging Inverse Problems'
git status --short
Get-Item -LiteralPath 'D:\DDM4IP-runtime\group-data\BDD100K_Blur_Sharp'
Get-Item -LiteralPath 'D:\DDM4IP-runtime\data-audit\bdd100k_proxy_metrics_20260902.csv'
Test-Path -LiteralPath 'D:\DDM4IP-runtime\group-data-views\BDD100K_Blur_Sharp'
~~~

Expected: DESKTOP-KBM1345 and final result False. Stop if destination exists.

- [x] **Step 2: Run the existing view-builder test**

~~~powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest tests.test_bdd100k_view_builder -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
~~~

Expected: hard-link and no-overwrite tests pass.

- [x] **Step 3: Create the view once**

~~~powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' .\scripts\build_bdd100k_views.py --source-root 'D:\DDM4IP-runtime\group-data\BDD100K_Blur_Sharp' --metrics-csv 'D:\DDM4IP-runtime\data-audit\bdd100k_proxy_metrics_20260902.csv' --destination 'D:\DDM4IP-runtime\group-data-views\BDD100K_Blur_Sharp' --seed 'ddm4ip-bdd100k-v1' --val-fraction 0.10
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
~~~

Expected summary: clean train/val 1565/174; noisy train/val 926/104; Q2/Q3 515/515.

- [x] **Step 4: Verify manifest and file counts**

~~~powershell
$view = 'D:\DDM4IP-runtime\group-data-views\BDD100K_Blur_Sharp'
Get-Content -Raw -LiteralPath "$view\summary.json"
@('train\clean','train\noisy','val\clean','val\noisy') | ForEach-Object {
  "$_=$((Get-ChildItem -LiteralPath (Join-Path $view $_) -File | Measure-Object).Count)"
}
~~~

Expected: exact counts from Step 3 and both summary.json and manifest.csv exist.

### Task 2: 用测试驱动支持 noisy-only Step 3

**Files:**
- Modify: ddm4ip\data\patch_dataset.py
- Modify: ddm4ip\trainers\deepinv_denoiser.py
- Modify: ddm4ip\losses\deepinv_loss.py
- Create: tests\test_noisy_only_patch_dataset.py
- Create: tests\test_deepinv_no_reference.py

**Consumes:** Existing DeepInvLoss.run_model behavior, which already accepts clean=None.

**Produces:** noisy-only batches, prediction/filter persistence without a clean assertion, and reprojection_l1/reprojection_l2 metrics.

- [ ] **Step 1: Add a failing PatchDataset regression test**

Use one temporary valid 16x16 RGB JPG and assert:

~~~python
dataset = PatchDataset(path=noisy_dir, degradation=None, split=Datasplit.TEST,
    dset_cfg=OmegaConf.create({
        "patch_size": 16, "x_flip": False, "full_test": False,
        "space_conditioning": False, "random_space_conditioning": False,
        "inflate_patches": 0, "cuda": False,
        "need_clean": False, "need_noisy": True,
    }), shuffle_clean=False)
batch = dataset[0]
assert batch.clean is None
assert batch.corrupt is not None
assert dataset.clean_img_size == dataset.corrupt_img_size
assert dataset.clean_conditioning_channels == dataset.corrupt_conditioning_channels
~~~

- [ ] **Step 2: Confirm current failure**

~~~powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest tests.test_noisy_only_patch_dataset -v
~~~

Expected before implementation: constructor fails because it always requests clean_patches.

- [ ] **Step 3: Implement the minimal dataset change**

In PatchDataset.__init__, pass self.need_clean and self.need_noisy to the initial get_next_patches probe instead of hard-coding both true. Derive corrupt dimensions from noisy_patches. If clean_patches is None, assign clean_img_size and clean_conditioning_channels from corrupt dimensions. Preserve every paired and clean+noisy code path.

- [ ] **Step 4: Add failing no-reference trainer/loss tests**

Use a fake loss returning a 1x3x16x16 prediction and 1x1x3x3 filters. For Batch(clean=None, corrupt=tensor), assert validate_batch creates img_00000.png and kernel_00000.pt when save_eval_to_file and save_pred_only are true. With an identity physics attached through object.__new__(DeepInvLoss), assert:

~~~python
metrics = loss.reprojection_metrics(torch.ones(1, 3, 4, 4), torch.zeros(1, 3, 4, 4))
assert metrics["reprojection_l1"].item() == 1.0
assert metrics["reprojection_l2"].item() == 1.0
~~~

- [ ] **Step 5: Implement no-reference output and residuals**

1. In DeepinvDenoiserTrainer.init_datasets use is_paired=False.
2. In validate_batch, use pred_img.cpu() whenever save_pred_only is true or val_batch.clean is None. Concatenate a clean target only if it exists.
3. Add DeepInvLoss.reprojection_metrics(x_recon, y_obs): apply already configured physics to x_recon on y_obs's device, return mean absolute and squared residuals.
4. In val_loss_with_output always append reprojection metrics; append LPIPS, PSNR and SSIM only if clean exists.

- [ ] **Step 6: Verify focused and complete tests**

~~~powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest tests.test_noisy_only_patch_dataset tests.test_deepinv_no_reference -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
~~~

Expected: all existing and new tests pass.

### Task 3: 添加 BDD100K Hydra 配置和组合测试

**Files:**
- Create: ddm4ip\configs\paths\bdd100k_runtime.yaml
- Create: ddm4ip\configs\dataset\bdd100k_noisy_patch.yaml
- Create: ddm4ip\configs\dataset\bdd100k_unpaired.yaml
- Create: ddm4ip\configs\exp\step1_bdd100k.yaml
- Create: ddm4ip\configs\exp\step2_bdd100k.yaml
- Create: ddm4ip\configs\exp\step3_bdd100k.yaml
- Create: tests\test_bdd100k_configs.py

**Consumes:** Step 1/2/3 parking-lot references and Task 1 view.

**Produces:** Three composition-tested BDD100K configs. Checkpoint/snapshot paths are injected by stage specs only after predecessor verification.

- [ ] **Step 1: Add failing config assertions**

Compose each experiment with paths=bdd100k_runtime. Assert:
- Step 1 uses patch, need_clean false, train/noisy and val/noisy.
- Step 2 uses simple_patch, independent clean/noisy paths, max_val_batches zero.
- Step 3 uses patch, need_clean false, training.train false, save_eval_to_file true and save_pred_only true.

- [ ] **Step 2: Add runtime paths**

~~~yaml
data: "D:/DDM4IP-runtime/group-data-views/BDD100K_Blur_Sharp"
out_path: "D:/DDM4IP-runtime/experiments/bdd100k-direct-transfer-20260903"
~~~

- [ ] **Step 3: Add noisy-only PatchDataset config**

~~~yaml
defaults:
 - degradation: no_degradation
 - noise: no_noise
name: patch
x_flip: false
patch_size: 64
inflate_patches: 0
num_patches_per_image: 64
patch_cache_size: 1024
space_conditioning: false
random_space_conditioning: false
random_replace_locmap: 0
full_test: false
cuda: false
need_clean: false
need_noisy: true
train_path: D:/DDM4IP-runtime/group-data-views/BDD100K_Blur_Sharp/train/noisy
test_path: D:/DDM4IP-runtime/group-data-views/BDD100K_Blur_Sharp/val/noisy
~~~

- [ ] **Step 4: Add Step 2 SimplePatchDataset config**

~~~yaml
defaults:
 - degradation: no_degradation
 - noise: no_noise
name: simple_patch
x_flip: false
patch_size: 64
inflate_patches: 13
space_conditioning: false
full_test: false
cuda: false
train_path: D:/DDM4IP-runtime/group-data-views/BDD100K_Blur_Sharp/train/clean
test_path: D:/DDM4IP-runtime/group-data-views/BDD100K_Blur_Sharp/val/clean
noisy_path: null
~~~

- [ ] **Step 5: Derive experiment configs**

Derive Step 1 from step1_parkinglot, replacing train/test datasets with bdd100k_noisy_patch and setting max_val_batches=0, num_workers=0, save_eval_to_file=false, exp_name=bdd100k_step1.

Derive Step 2 from step2_parkinglot, replacing train/test datasets with bdd100k_unpaired. Set dataset.train.noisy_path to train/noisy, dataset.test.noisy_path to val/noisy, max_val_batches=0, num_workers=0, save_eval_to_file=false, exp_name=bdd100k_step2.

Derive Step 3 from step3_parkinglot, replacing test dataset with bdd100k_noisy_patch. Set batch_size=1, num_workers=0, save_eval_to_file=true, save_pred_only=true, exp_name=bdd100k_step3.

- [ ] **Step 6: Resolve without training**

~~~powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest tests.test_bdd100k_configs -v
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m ddm4ip.main exp=step1_bdd100k paths=bdd100k_runtime --cfg job --resolve
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m ddm4ip.main exp=step2_bdd100k paths=bdd100k_runtime --cfg job --resolve
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m ddm4ip.main exp=step3_bdd100k paths=bdd100k_runtime --cfg job --resolve
~~~

Expected: every command exits zero and starts no training.

### Task 4: 创建计划任务运行器

**Files:**
- Create at runtime: D:\DDM4IP-runtime\orchestration\run_bdd100k_stage.ps1
- Create at runtime: D:\DDM4IP-runtime\orchestration\start_bdd100k_task.ps1
- Create at runtime: D:\DDM4IP-runtime\orchestration\step-spec.schema.json

**Consumes:** JSON fields task_name, stage, run_root, hydra_overrides, expected_artifacts and mode.

**Produces:** A Scheduled Task with a stage-local status.json, append-only task.log, command.txt, resolved-config.yaml and copied JSON spec.

- [ ] **Step 1: Enforce the runner contract**

Reject missing JSON fields, stage outside step1/step2/step3, mode outside pilot/full, a run root outside D:\DDM4IP-runtime\experiments, a pre-existing stage root, or missing predecessor artifact.

- [ ] **Step 2: Implement state transitions**

Write RUNNING before configuration resolution. Status JSON always includes state, step, detail, updated_at, host, python, repository, runtime_root, stage_root, task_name, log_path, config_path, output_path, process_id and exit_code. Resolve configuration into resolved-config.yaml before launching Python. Execute normal command with output appended to task.log. Declare SUCCESS only after native exit code zero and every expected artifact exists.

- [ ] **Step 3: Make native exit handling safe**

Temporarily set ErrorActionPreference to Continue around each Python command, capture LASTEXITCODE, restore the old preference in finally, and write FAILED with the original native exit code if nonzero. Set all five cache/temp variables only inside the runner process.

- [ ] **Step 4: Register safely and parser-test**

The launcher rejects an existing task name, registers an on-demand task that invokes run_bdd100k_stage.ps1 with one JSON spec, and starts it. Parse both scripts with System.Management.Automation.Language.Parser. Use one deliberately incomplete test spec in a new temporary runtime directory; expect FAILED at validate-spec and no Python process.

### Task 5: 运行短 pilot 并估时

**Files:**
- Create at runtime: step1-pilot.json, step2-pilot.json, step3-pilot.json
- Create at runtime: pilot-summary.json for each stage

**Consumes:** Passed tests/configs, Task 1 view and verified predecessor pilot artifact.

**Produces:** Per-stage speed, peak GPU memory, checkpoint/output proof and full-run estimate.

- [ ] **Step 1: Apply the pilot budget formula**

For global batch B, run 64 optimizer updates: max_steps=64*B, report_every_steps=16*B, plot_every_steps=64*B, save_every_steps=64*B, save_first_step=true. Start B=1 and num_workers=0. If peak GPU memory is below 6.0 GiB, run a new pilot with 2B. Stop at first failed task or peak memory at least 6.0 GiB. Select the largest successful B below 7.2 GiB.

- [ ] **Step 2: Launch Step 1 pilot**

Use DDM4IP-BDD100K-Step1-Pilot, exp=step1_bdd100k, paths=bdd100k_runtime and a root ending in -pilot\step1. Require its final training-state artifact. Confirm only once after dispatch:

~~~powershell
Get-ScheduledTask -TaskName 'DDM4IP-BDD100K-Step1-Pilot' | Get-ScheduledTaskInfo
Get-Content -Raw -LiteralPath 'D:\DDM4IP-runtime\experiments\bdd100k-direct-transfer-20260903-pilot\step1\status.json'
Get-Content -LiteralPath 'D:\DDM4IP-runtime\experiments\bdd100k-direct-transfer-20260903-pilot\step1\task.log' -Tail 50
~~~

If RUNNING with advancing log, stop checking and give the user these commands with -Wait.

- [ ] **Step 3: Gate Step 2 and Step 3 pilots**

After user-reported completion, independently require SUCCESS, exit code zero, resolved config, completion marker, expected artifact and elapsed time. Step 2 receives only the verified Step 1 pilot checkpoint and uses max_val_batches=0. Step 3 receives only the verified Step 2 pilot snapshot and requires predictions, filters, and no paired metric labels.

- [ ] **Step 4: Apply the three-window estimate gate**

Estimate Step 1 and Step 2 from 17 Mi and 8 Mi reference image budgets divided by selected global batch; estimate Step 3 from held-out images per second. If a stage exceeds the 10.5-hour per-window estimate, do not start it. Report the calculation and one explicit divisible smaller budget, then wait for user approval. A window may start during daytime or nighttime.

### Task 6: 运行三阶段完整基线

**Files:**
- Create at runtime: step1-full.json, step2-full.json, step3-full.json
- Create at runtime: D:\DDM4IP-runtime\experiments\bdd100k-direct-transfer-20260903\baseline-summary.json

**Consumes:** User-approved pilot estimates and verified predecessor artifacts.

**Produces:** Full Step 1 checkpoint, full Step 2 snapshot, Step 3 predictions/filters and complete provenance.

- [ ] **Step 1: Launch full Step 1**

Use DDM4IP-BDD100K-Step1-Full with only the approved batch/update budget. Save at final step and save_first_step=true. Confirm once, then provide:

~~~powershell
Get-Content -Raw -LiteralPath 'D:\DDM4IP-runtime\experiments\bdd100k-direct-transfer-20260903\step1\status.json'
Get-Content -LiteralPath 'D:\DDM4IP-runtime\experiments\bdd100k-direct-transfer-20260903\step1\task.log' -Tail 50 -Wait
~~~

- [ ] **Step 2: Verify Step 1 before full Step 2**

After user reports completion, require SUCCESS, exit code zero, one completion marker, final checkpoint, resolved config and checkpoint SHA-256. Use that exact checkpoint only in DDM4IP-BDD100K-Step2-Full; keep max_val_batches=0.

- [ ] **Step 3: Verify Step 2 before full Step 3**

Require the verified final network snapshot and SHA-256. Use that exact snapshot only in DDM4IP-BDD100K-Step3-Full with training.train=false, batch_size=1, save_eval_to_file=true and save_pred_only=true.

- [ ] **Step 4: Write provenance**

baseline-summary.json records view and audit hashes, task names, stage timestamps, exit codes, config hashes, predecessor hashes, output counts, GPU identity and paired_reference_metrics=unavailable.

### Task 7: 生成无参考结果包

**Files:**
- Create at runtime: evaluation\fixed-sample-manifest.json
- Create at runtime: evaluation\reprojection-summary.json
- Create at runtime: evaluation\failure-review.md

**Consumes:** Step 3 predictions, filters, reprojection scalars and immutable manifest.

**Produces:** Fixed samples, self-consistency statistics and one evidence-based next change.

- [ ] **Step 1: Fix samples before inspection**

Hash manifest.csv and select 24 held-out noisy entries: eight from each third of the Laplacian ranking. Save input, prediction and filter paths before opening results.

- [ ] **Step 2: Export residual evidence**

Write count, mean, median, fifth and 95th percentiles of reprojection_l1 and reprojection_l2. State that these quantify learned-model self-consistency, not hidden clean-image accuracy.

- [ ] **Step 3: Use one failure rubric**

For every sample assign one or more labels: recovery_insufficient, over_sharpen_or_hallucinated_texture, color_or_exposure_shift, nonuniform_blur_mismatch, strong_degradation_collapse, cross_scene_instability, no_obvious_artifact. Do not replace failed examples.

- [ ] **Step 4: Write one next modification**

failure-review.md has execution evidence, observed behavior and exactly one next direction: narrower blur strata, explicit degradation-family change, or training-objective adjustment. It states that paired PSNR, SSIM and LPIPS are unavailable and sharpness alone is not proof.

## Final Verification Checklist

- [ ] Data view counts match Task 1 and no existing view was overwritten.
- [ ] Full unittest discovery passes after code/config changes.
- [ ] All BDD100K Hydra configurations resolve without training.
- [ ] Every stage has a unique task name, root, status.json, task.log, command.txt and resolved-config.yaml.
- [ ] No successor stage starts before independent predecessor verification.
- [ ] No stage above 10.5 hours starts without recorded user approval.
- [ ] Final report contains no paired-reference claim and preserves failure evidence.
- [ ] WORKLOG.md records only verified outcomes, paths, hashes, exit codes and failure evidence.
