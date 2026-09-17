# BDD100K Known-Motion-Blur Quantitative Reproduction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不改变既有真实 BDD100K 不配对主线的前提下，构建一条可审计、可重放的 BDD100K 已知固定运动模糊 synthetic quantitative 主线，并合法产出 input、oracle、5 个 learned seed 的逐图 PSNR/SSIM/LPIPS 与核指标。

**Architecture:** 新主线以独立 benchmark 根和独立 Hydra 配置接入：先冻结源清单，再通过项目 `Blur` 物理算子生成固定 noisy PNG 和显式 pairs manifest；Step 1 使用 noisy-only，Step 2 使用 clean-only，Step 3 使用 manifest-paired。逐图指标由专用记录器写入不可覆盖的 JSONL/summary，仓库外的 synthetic runner 只接受冻结 spec、独立核验 benchmark/checkpoint 哈希，并通过 Windows 任务计划程序运行所有耗时阶段。

**Tech Stack:** Python 3.10 (`E:\Anaconda3\envs\ddm4ip\python.exe`); PyTorch 2.4.1+cu118; DeepInv 0.4.2; Hydra/OmegaConf; Pillow; torchvision; scikit-image; LPIPS AlexNet; Windows PowerShell 5.1; Windows Task Scheduler; `unittest`.

**Spec:** `docs/superpowers/specs/2026-09-06-bdd100k-known-blur-quantitative-reproduction-design.md`

## Global Constraints

- 所有仓库文件读取、修改、测试和 Git 检查只在 SSH 主机 `group-pc` 的 `D:\Unsupervised Imaging Inverse Problems` 执行；每次新对话先确认 `hostname` 为 `DESKTOP-KBM1345`。
- 当前远端 `WORKLOG.md` 不存在且 Git 状态为 `AD WORKLOG.md`；用户明确处理前不得恢复、创建或覆盖它。计划实施期间只能在阶段交接中报告这一风险。
- 远端 Git 仅允许 `status`、`diff`、`log` 等只读操作；不得 add、commit、push、pull、rebase、切换分支或配置凭据。本计划中的每个“审查门”取代常规 commit 步骤。
- 保留当前全部未提交修改；实现前逐文件记录 SHA-256，上传或写回前重新比较，发生并发变化立即停止。
- 不覆盖或改名 `step{1,2,3}_bdd100k.yaml`、真实 Q2/Q3 视图、noisy-only 指标边界、旧运行器或历史实验目录。
- 项目入口固定为 `E:\Anaconda3\envs\ddm4ip\python.exe -m ddm4ip.main`；不得在本机运行项目测试、数据处理、训练或评估。
- 项目进程只设置进程级 `TEMP`、`TMP`、`PIP_CACHE_DIR`、`TORCH_HOME`、`XDG_CACHE_HOME`、`MPLCONFIGDIR`、`PYTHONPYCACHEPREFIX` 到 `D:\DDM4IP-runtime` 的项目专用目录，不修改全局环境。
- 数据源固定为 clean hard-link view 的 `train\clean` 1,565 张与 `val\clean` 174 张；源 view `manifest.csv` 的既有独立核验 SHA-256 为 `6BA1F476AFAEFACA60A9B6EDFB7DB2740BF99D355C12F49335FFB6C342724886`。
- 数据角色固定为 `split_seed=42` 的 1,000/100/500/139；预处理固定为 `[0,280,720,1000]` 中央 720×720、Pillow bicubic 到 256×256、RGB PNG、无增强。
- 真实退化固定为 `motion_blur`, `kernel_size=32`, `intensity=0.5`, `rnd_seed=1`, `noise_std=0.02`, `padding=replicate`；生成公式为 `clamp(A_k(x)+epsilon,0,1)`。
- benchmark 根固定为 `D:\DDM4IP-runtime\synthetic-benchmarks\bdd100k-motionblur-v1`；实验根固定为 `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1`。任一目标已存在均拒绝执行，不先删后建。
- 正式指标固定为整张 RGB `[0,1]` 的逐图 PSNR、`data_range=1/channel_axis=0` SSIM、AlexNet LPIPS `normalize=True`；输出先 clamp，不做事后边缘裁剪。
- Oracle 和 learned 使用同一 `dpir_bdd100k_256` 求解器配置；两者唯一差异是 `kernel-gt.pt` 与经核验 Step 2 snapshot。
- Step 2 正式随机种子固定为 `[0, 1, 2, 3, 4]`，共用同一个经核验 Step 1 terminal checkpoint；不得在未获用户书面批准时减少种子数或训练预算。
- 所有数据构建、权重准备、GPU pilot、训练和正式评估必须在新的明确授权对话中由 Windows 任务计划程序托管；启动后只做一次任务、进程、日志与状态更新确认，不持续轮询。
- 本计划当前仅被授权写入计划文档；Tasks 1–8 属于后续“代码与无训练测试”阶段，Tasks 9–14 各自仍受文中授权门约束。

## File and Responsibility Map

### Repository files to create

- `ddm4ip/benchmarks/__init__.py` — 导出 synthetic benchmark 的稳定公共接口。
- `ddm4ip/benchmarks/bdd100k_synthetic.py` — 源清单、确定性划分、预处理、冻结核、噪声种子、派生文件与清单构建的纯逻辑。
- `scripts/build_bdd100k_synthetic_benchmark.py` — `inspect`/`build` 薄 CLI；不复制算法。
- `ddm4ip/data/manifest_paired_dataset.py` — 对 `pairs.jsonl` 做路径、ID、尺寸、哈希和一一对应验证，并返回显式配对 `Batch`。
- `ddm4ip/utils/benchmark_metrics.py` — 标量化图像指标、核指标、规范 JSON 哈希、不可覆盖逐图记录与确定性聚合。
- `scripts/analyze_bdd100k_synthetic_kernel.py` — 只读加载 Step 2 snapshot 与 `kernel-gt.pt`，输出 kernel PSNR/NCC JSON。
- `scripts/aggregate_bdd100k_synthetic_results.py` — 校验 1 个 oracle 与 5 个 learned summary 后生成跨 seed 汇总。
- `scripts/bdd100k_synthetic_runner.py` — versioned synthetic spec validation, command freezing, stage execution, and artifact verification; it never starts a Scheduled Task itself.
- `ddm4ip/configs/paths/bdd100k_synthetic_runtime.yaml` — synthetic 数据根和实验根。
- `ddm4ip/configs/dataset/bdd100k_synthetic_noisy.yaml` — Step 1 noisy-only 256×256 数据。
- `ddm4ip/configs/dataset/bdd100k_synthetic_clean.yaml` — Step 2 clean-only 256×256 数据与固定噪声水平。
- `ddm4ip/configs/dataset/bdd100k_synthetic_paired.yaml` — Step 3 manifest-paired 数据和 frozen file blur。
- `ddm4ip/configs/dataset/degradation/file_blur.yaml` — 从 `kernel-gt.pt` 加载固定 Blur。
- `ddm4ip/configs/models/dpir_bdd100k_256.yaml` — Oracle/learned 共用的 DPIR/DRUNet 参数。
- `ddm4ip/configs/exp/step1_bdd100k_synthetic.yaml`, `step2_bdd100k_synthetic.yaml`, `step3_bdd100k_oracle.yaml`, `step3_bdd100k_synthetic.yaml` — 四个隔离实验入口。
- `tests/test_file_blur.py`, `tests/test_bdd100k_synthetic_builder.py`, `tests/test_manifest_paired_dataset.py`, `tests/test_bdd100k_synthetic_data_boundaries.py`, `tests/test_benchmark_metrics.py`, `tests/test_bdd100k_synthetic_trainer.py`, `tests/test_bdd100k_synthetic_configs.py`, `tests/test_bdd100k_synthetic_runner.py` — 对应红绿回归。

### Repository files to modify

- `ddm4ip/degradations/degradation.py:30-40,43-90` — `.pt` tensor loader 与 `file_blur` 工厂分支。
- `ddm4ip/data/base.py:178-234` — 注册 `manifest_paired` 数据集。
- `ddm4ip/data/patch_dataset.py:63-148,430-437` — clean-only 路径不读取 noisy，并支持独立 `noise_level_override`。
- `ddm4ip/losses/deepinv_loss.py:166-212` — 复用同一 Alex LPIPS 实例返回严格逐样本标量。
- `ddm4ip/trainers/deepinv_denoiser.py:32-54,253-323` — synthetic recorder 分支；既有 real manifest 分支保持原样。
- `tests/test_bdd100k_configs.py`, `tests/test_deepinv_no_reference.py`, `tests/test_step3_geometry_provenance.py` — 只增加保护断言，确认旧主线未变。

### Runtime-only files to create; do not place in Git

- `D:\DDM4IP-runtime\orchestration\synthetic-step-spec.schema.json`
- `D:\DDM4IP-runtime\orchestration\run_bdd100k_synthetic_stage.ps1`
- `D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1`

---

### Task 1: Add frozen `.pt` file-blur support

**Files:**
- Create: `tests/test_file_blur.py`
- Create: `ddm4ip/configs/dataset/degradation/file_blur.yaml`
- Modify: `ddm4ip/degradations/degradation.py:30-40,43-90`

**Interfaces:**
- Consumes: a plain finite float tensor saved at `kernel-gt.pt`, shaped `H×W`, `1×H×W`, or `1×1×H×W`.
- Produces: `load_filter_from_file(path: str | Path, kernel_size: int | None = None) -> torch.Tensor` returning `1×1×H×W`, and `instantiate_single_kernel({kind: file_blur, kernel_path, padding}, noise_model) -> Blur`.

- [ ] **Step 1: Write failing `.pt` loader and Blur behavior tests**

```python
class FileBlurTests(unittest.TestCase):
    def test_pt_kernel_loads_without_rotation_or_renormalization(self):
        kernel = torch.arange(1, 17, dtype=torch.float32).reshape(4, 4)
        kernel /= kernel.sum()
        torch.save(kernel, self.root / "kernel.pt", _use_new_zipfile_serialization=False)
        loaded = load_filter_from_file(self.root / "kernel.pt", kernel_size=None)
        self.assertEqual(tuple(loaded.shape), (1, 1, 4, 4))
        torch.testing.assert_close(loaded[0, 0], kernel, rtol=0, atol=0)

    def test_file_blur_rejects_nan_negative_and_nonunit_kernels(self):
        for kernel in (torch.tensor([[float("nan")]]), torch.tensor([[-1.0]]), torch.ones(2, 2))):
            torch.save(kernel, self.root / "bad.pt", _use_new_zipfile_serialization=False)
            with self.assertRaises(ValueError):
                load_filter_from_file(self.root / "bad.pt", kernel_size=None)
```

- [ ] **Step 2: Run the focused test and capture the expected red result**

```powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest tests.test_file_blur -v
if ($LASTEXITCODE -eq 0) { throw 'Expected the new file_blur tests to fail before implementation' }
```

Expected: `.pt` raises the current “Only mat files are supported” error or `file_blur` is unrecognized.

- [ ] **Step 3: Implement minimal canonical tensor loading and validation**

```python
def load_filter_from_file(path, kernel_size: int | None = None):
    path = Path(path)
    if path.suffix == ".pt":
        kernel = torch.load(path, map_location="cpu", weights_only=True)
        if not isinstance(kernel, torch.Tensor):
            raise TypeError(".pt kernel must contain one tensor")
        kernel = kernel.detach().to(dtype=torch.float32, device="cpu")
        while kernel.ndim < 4:
            kernel = kernel.unsqueeze(0)
        if kernel.ndim != 4 or kernel.shape[:2] != (1, 1):
            raise ValueError("file blur kernel must canonicalize to 1x1xHxW")
    elif path.suffix == ".mat":
        kernel = torch.from_numpy(scipy.io.loadmat(path)["Kernel"]).float()[None, None]
    else:
        raise ValueError(f"Unsupported kernel file: {path.suffix}")
    if not torch.isfinite(kernel).all() or (kernel < 0).any():
        raise ValueError("kernel must be finite and nonnegative")
    if not torch.isclose(kernel.sum(), torch.tensor(1.0), rtol=1e-6, atol=1e-6):
        raise ValueError("kernel must sum to one")
    return pad_kernel(kernel, kernel_size) if kernel_size is not None else kernel
```

Add `file_blur` to `instantiate_single_kernel` with `filter=load_filter_from_file(pert_cfg["kernel_path"], pert_cfg.get("kernel_size"))`, then return `Blur(filter=filter, padding=pert_cfg.get("padding", "replicate"), noise_model=noise_model)`.

- [ ] **Step 4: Add the frozen config group**

```yaml
kind: file_blur
kernel_path: ${paths.data}/degradation/kernel-gt.pt
kernel_size: null
padding: replicate
```

- [ ] **Step 5: Run focused and compatibility tests**

```powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest tests.test_file_blur tests.test_internal_package_imports -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

- [ ] **Step 6: Review gate**

Run `git diff -- ddm4ip/degradations/degradation.py ddm4ip/configs/dataset/degradation/file_blur.yaml tests/test_file_blur.py` and confirm no existing motion-blur, downsampling, or `.mat` behavior was removed. Do not stage or commit.

### Task 2: Freeze source inventory and deterministic role assignment

**Files:**
- Create: `ddm4ip/benchmarks/__init__.py`
- Create: `ddm4ip/benchmarks/bdd100k_synthetic.py`
- Create: `tests/test_bdd100k_synthetic_builder.py`

**Interfaces:**
- Produces `SourceRecord(source_id: str, source_relpath: str, size_bytes: int, sha256: str, width: int, height: int, channels: int)`.
- Produces `inspect_sources(view_root: Path, expected_view_manifest_sha256: str) -> tuple[list[SourceRecord], str]`; returned hash is SHA-256 of UTF-8 CSV bytes with fixed header/order.
- Produces `split_sources(records: Sequence[SourceRecord], split_seed: int = 42) -> dict[str, list[SourceRecord]]` with keys `step1_observation`, `step2_clean`, `test_paired`, `dev_reserve`.

- [ ] **Step 1: Write failing inventory validation tests**

Use valid 1280×720 RGB fixture PNGs placed under `train/clean` and `val/clean`; write a view manifest with clean rows. Assert that `inspect_sources`:

```python
view_digest = hashlib.sha256((view_root / "manifest.csv").read_bytes()).hexdigest()
records, digest = inspect_sources(view_root, view_digest)
self.assertEqual([r.source_id for r in records], sorted(r.source_id for r in records))
self.assertEqual({(r.width, r.height, r.channels) for r in records}, {(1280, 720, 3)})
self.assertRegex(digest, r"^[0-9a-f]{64}$")
```

Add separate tests that reject: wrong view-manifest SHA, duplicate filename/source ID across train and val, duplicate content SHA under different IDs, non-1280×720 input, decode failure, non-RGB input, and a count other than the caller-provided expected count.

- [ ] **Step 2: Write failing 1,739-way split test without allocating images**

```python
records = [SourceRecord(f"id-{i:04d}", f"train/clean/id-{i:04d}.jpg", 1,
          hashlib.sha256(str(i).encode()).hexdigest(), 1280, 720, 3) for i in range(1739)]
roles = split_sources(records, split_seed=42)
self.assertEqual({k: len(v) for k, v in roles.items()}, {
    "step1_observation": 1000, "step2_clean": 100,
    "test_paired": 500, "dev_reserve": 139,
})
self.assertEqual(set().union(*(set(r.source_id for r in v) for v in roles.values())),
                 {r.source_id for r in records})
self.assertEqual(split_sources(records, 42), roles)
self.assertNotEqual(split_sources(records, 43), roles)
```

- [ ] **Step 3: Run the focused test and verify red**

```powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest tests.test_bdd100k_synthetic_builder -v
if ($LASTEXITCODE -eq 0) { throw 'Expected builder tests to fail before module creation' }
```

- [ ] **Step 4: Implement canonical inventory bytes**

Use normalized forward-slash paths, `source_id=Path(filename).stem`, lexicographic path sorting, streaming SHA-256, Pillow decode with `image.load()`, and a CSV header fixed to:

```python
SOURCE_FIELDS = (
    "source_id", "source_relpath", "size_bytes", "sha256",
    "width", "height", "channels",
)
```

Hash the exact `lineterminator="\n"` UTF-8 CSV bytes. Validate the expected view-manifest hash and all source files before returning any record. Reject duplicate `source_id` and duplicate content SHA instead of attempting to group or delete them.

- [ ] **Step 5: Implement deterministic split by seeded permutation**

Use `random.Random(split_seed).shuffle(indices)` over records already sorted by `source_relpath`; slice exactly `[0:1000]`, `[1000:1100]`, `[1100:1600]`, `[1600:1739]`, then sort each role by `source_id` for stable output manifests.

- [ ] **Step 6: Run focused tests and review exact public exports**

```powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest tests.test_bdd100k_synthetic_builder -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
git diff -- ddm4ip/benchmarks tests/test_bdd100k_synthetic_builder.py
```

Do not stage or commit.

### Task 3: Build deterministic PNG, kernel, noisy observations, and manifests

**Files:**
- Modify: `ddm4ip/benchmarks/bdd100k_synthetic.py`
- Create: `scripts/build_bdd100k_synthetic_benchmark.py`
- Extend: `tests/test_bdd100k_synthetic_builder.py`

**Interfaces:**
- Produces `preprocess_image(source: Path) -> torch.Tensor` shaped `3×256×256`, float32 `[0,1]`.
- Produces `make_noise_seed(role: str, source_id: str) -> int` using the first 8 bytes of SHA-256 for `bdd100k-motionblur-v1\0{role}\0{source_id}`, reduced modulo `2**31`.
- Produces `build_benchmark(records, expected_source_manifest_sha256, destination, split_seed=42) -> dict[str, object]`.
- CLI subcommand `inspect` requires `--view-root`, `--expected-view-manifest-sha256`, `--expected-source-count`, and `--output-manifest`; subcommand `build` requires those inputs plus `--source-manifest`, `--expected-source-manifest-sha256`, and `--destination`.

- [ ] **Step 1: Add failing crop/resize tests**

Create a coordinate-coded 1280×720 RGB image and compare `preprocess_image` to a direct Pillow reference using:

```python
expected = image.crop((280, 0, 1000, 720)).resize(
    (256, 256), resample=Image.Resampling.BICUBIC
).convert("RGB")
```

Assert exact `3×256×256`; reject any wrong input size rather than padding or skipping.

- [ ] **Step 2: Add failing kernel and deterministic observation tests**

Generate the true physics only through:

```python
physics = instantiate_single_kernel(
    {"kind": "motion_blur", "kernel_size": 32, "intensity": 0.5, "rnd_seed": 1},
    noise_model=None,
)
```

Assert kernel shape `1×1×32×32`, finite, nonnegative, sum one, nonzero support larger than one pixel, and identical canonical tensor hash in two fresh destinations. Save with legacy serialization for stable file bytes:

```python
torch.save(kernel.cpu(), path, _use_new_zipfile_serialization=False)
```

Reload that saved file through Task 1 `file_blur`; generate noise with a CPU `torch.Generator().manual_seed(noise_seed)` and assert two builds have byte-identical noisy PNGs. Assert changing `source_id` changes `noise_seed`.

- [ ] **Step 3: Add failing no-overwrite and preflight-failure tests**

Assert `build_benchmark` leaves `destination` absent when source count, expected source-manifest SHA, source SHA, dimensions, decode, or duplicate ID fails. After a successful fixture build, rerunning against the same destination must raise `FileExistsError` and preserve every existing file hash.

- [ ] **Step 4: Implement preflight then one-shot build**

Preflight all 1,739 records and expected inventory SHA before `destination.mkdir`. After creation, write:

```text
source-manifest.csv
split-manifest.csv
summary.json
preprocessing.json
status.json
build.log
degradation/kernel-gt.pt
degradation/kernel-gt.png
degradation/degradation.json
step1-observation/noisy/*.png
step2-clean/clean/*.png
test-paired/clean/*.png
test-paired/noisy/*.png
test-paired/pairs.jsonl
dev-reserve/clean/*.png
dev-reserve/noisy/*.png
dev-reserve/pairs.jsonl
```

Each pair row uses relative paths under its role directory and fields:

```python
PAIR_FIELDS = (
    "schema_version", "role", "source_id", "source_relpath", "source_sha256",
    "clean_path", "clean_sha256", "noisy_path", "noisy_sha256", "noise_seed",
    "source_size", "crop_box", "output_size", "channels", "kernel_tensor_sha256",
)
```

`summary.json` records every manifest/config/file SHA, exact role counts, source view-manifest SHA, source inventory SHA, kernel tensor/file SHA, preprocessing, degradation, Python/Pillow/PyTorch/DeepInv versions, and `implementation_difference="fixed saved Step 1 noise rather than online resampling"`.

- [ ] **Step 5: Implement CLI separation**

`inspect` accepts `--view-root`, `--expected-view-manifest-sha256`, `--expected-source-count 1739`, and `--output-manifest`; it refuses an existing output file and never creates the benchmark root. `build` additionally requires `--source-manifest`, `--expected-source-manifest-sha256`, and `--destination`; it rehashes every source against the approved manifest before writing.

- [ ] **Step 6: Run builder tests**

```powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest tests.test_bdd100k_synthetic_builder -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

- [ ] **Step 7: Review gate**

Confirm tests never touch the real view or fixed benchmark path, no SciPy/Pillow convolution exists, and production code calls `instantiate_single_kernel` plus frozen `.pt` reload. Do not execute either CLI on real data in this phase.

### Task 4: Add clean-only and manifest-paired dataset contracts

**Files:**
- Create: `ddm4ip/data/manifest_paired_dataset.py`
- Modify: `ddm4ip/data/base.py:178-234`
- Modify: `ddm4ip/data/patch_dataset.py:63-148,169-212,282-318,370-437`
- Create: `tests/test_manifest_paired_dataset.py`
- Create: `tests/test_bdd100k_synthetic_data_boundaries.py`

**Interfaces:**
- Produces `ManifestPairedDataset(path, degradation, split, dset_cfg, shuffle_clean=False, generator=None)`.
- `ManifestPairedDataset.__getitem__(index) -> Batch` returns clean/corrupt `3×256×256`, `kernel=None`, and complete scalar/string/tensor metadata.
- `PatchDataset.noise_level` honors `noise_level_override` even when `corruption is None`.

- [ ] **Step 1: Write failing manifest-paired happy-path test**

Create two clean/noisy PNG pairs plus `pairs.jsonl`. Initialize through `init_dataset` with `name=manifest_paired`. Assert explicit IDs, tensors, no reordering, no extra degradation, and metadata survives `Batch.collate_fn([dataset[0], dataset[1]]).to("cpu")[1:]`:

```python
self.assertEqual(batch.meta["source_id"], ["source-1"])
self.assertEqual(batch.meta["clean_sha256"], [sha256(clean_1)])
self.assertEqual(batch.meta["noisy_sha256"], [sha256(noisy_1)])
self.assertEqual(batch.meta["noise_seed"].tolist(), [101])
self.assertEqual(tuple(batch.clean.shape), (1, 3, 256, 256))
self.assertEqual(tuple(batch.corrupt.shape), (1, 3, 256, 256))
```

- [ ] **Step 2: Write failing fail-closed dataset tests**

Separate tests must reject before the first sample is returned: missing file, absolute/out-of-root path, reparse-point component, duplicate `source_id`, duplicate clean/noisy path, wrong hash, mismatched row ID/path stem, wrong `role`, wrong dimensions, unequal clean/noisy dimensions, unexpected JSON key, and two rows referencing the same source.

- [ ] **Step 3: Write failing Step 1/Step 2 exposure tests**

```python
step1 = PatchDataset(noisy_dir, None, Datasplit.TRAIN, noisy_only_cfg, shuffle_clean=True)
self.assertIsNone(step1[0].clean)
self.assertIsNotNone(step1[0].corrupt)

step2 = PatchDataset(clean_dir, None, Datasplit.TRAIN, clean_only_cfg, shuffle_clean=True)
self.assertIsNotNone(step2[0].clean)
self.assertIsNone(step2[0].corrupt)
self.assertIsNone(step2[0].kernel)
self.assertEqual(step2[0].noise_level.item(), 0.02)
```

Patch `BaseImageFolderDataset` on the unused side to raise immediately; this proves Step 1 never reads clean and Step 2 never reads noisy/test data.

- [ ] **Step 4: Run focused tests and verify red**

```powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest tests.test_manifest_paired_dataset tests.test_bdd100k_synthetic_data_boundaries -v
if ($LASTEXITCODE -eq 0) { throw 'Expected new dataset tests to fail before implementation' }
```

- [ ] **Step 5: Implement `ManifestPairedDataset` validation and loading**

At construction, parse every nonempty JSONL line, require exactly `PAIR_FIELDS`, enforce relative containment and no reparse points, verify all hashes and 256×256 RGB dimensions, and build immutable row objects. `max_imgs` may select only the first N rows for a fixed dev pilot; it never reshuffles. Expose `clean_img_size=corrupt_img_size=(3,256,256)`, conditioning channels zero, label dimension zero, and `noise_level` from the configured `file_blur` noise model.

- [ ] **Step 6: Implement unused-side suppression in `PatchDataset`**

Construct `clean_full_data` only when `need_clean`; construct `noisy_full_data` only when `need_noisy`. Remove the equal-length requirement when only one side is requested. Set `dset_length` and source IDs from the requested side, and have `noise_level` return `torch.tensor(float(dset_cfg["noise_level_override"]))` when supplied.

- [ ] **Step 7: Register the dataset and run tests**

```python
elif dset_name == "manifest_paired":
    from .manifest_paired_dataset import ManifestPairedDataset
    return ManifestPairedDataset(data_path, degradation=perturbation,
                                 shuffle_clean=False, dset_cfg=dset_cfg, split=split)
```

```powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest tests.test_manifest_paired_dataset tests.test_bdd100k_synthetic_data_boundaries tests.test_noisy_only_patch_dataset -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

- [ ] **Step 8: Review gate**

Verify the real `PatchDataset` full-image provenance fields and `SimplePatchDataset` unequal-length behavior are untouched. Do not instantiate the real benchmark.

### Task 5: Add deterministic per-image metrics, kernel analysis, and cross-seed aggregation

**Files:**
- Create: `ddm4ip/utils/benchmark_metrics.py`
- Create: `scripts/analyze_bdd100k_synthetic_kernel.py`
- Create: `scripts/aggregate_bdd100k_synthetic_results.py`
- Create: `tests/test_benchmark_metrics.py`
- Modify: `ddm4ip/losses/deepinv_loss.py:166-172,202-212`

**Interfaces:**
- Produces `compute_image_metrics(reference, estimate, lpips_model) -> dict[str, float]`.
- Produces `compute_kernel_metrics(estimated, truth) -> dict[str, float]` with keys `kernel_psnr`, `kernel_ncc`.
- Produces `canonical_json_sha256(value: Mapping[str, object]) -> str`.
- Produces `BenchmarkMetricWriter(output_dir: Path, experiment_id: str, variant: Literal["oracle","learned"], step2_seed: int | None, solver_config_sha256: str, kernel_gt_path: Path, expected_count: int)` with `prepare_record(batch_meta: Mapping[str, object], prediction: torch.Tensor, filters: torch.Tensor, prediction_name: str, kernel_name: str, solver_geometry: Mapping[str, object], input_metrics: Mapping[str, float], restored_metrics: Mapping[str, float]) -> str`, `append(serialized_row: str) -> None`, and `write_summary() -> dict[str, object]`.

- [ ] **Step 1: Write failing image metric tests**

Use a small injected LPIPS stub that returns mean absolute difference, plus a mock around `lpips.LPIPS`, to avoid downloads while asserting `net="alex"` and `normalize=True`. Assert identical tensors give PSNR above 150 dB, SSIM exactly 1, LPIPS 0; a controlled perturbation lowers PSNR/SSIM and raises LPIPS. Assert batch size greater than one is rejected by the per-image API rather than averaged silently.

- [ ] **Step 2: Write failing kernel alignment tests**

Create a normalized 32×32 truth and identical 28×28 center crop. Assert `compute_kernel_metrics` calls the existing `equate_kernel_shapes` center-padding rule, yields finite values, NCC near 1 for aligned kernels, and a deliberately shifted kernel has lower NCC. No search over offsets is permitted.

- [ ] **Step 3: Write failing writer/aggregation tests**

Prepare three records with known values. Assert `metrics.jsonl` has one line per source and `summary.json` contains count, population standard deviation, median, min, max, and failures=0 for every metric. Recompute all statistics independently in the test. Assert NaN, duplicate source ID, wrong seed, wrong expected count, existing output, or mismatched solver/kernel/benchmark hash is rejected.

For cross-seed aggregation, require exactly one oracle summary and learned seeds `{0,1,2,3,4}`; reject duplicates/missing seeds, unequal sample counts, unequal source-set hash, unequal solver config hash, or unequal `kernel_gt_sha256`.

- [ ] **Step 4: Run focused tests and verify red**

```powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest tests.test_benchmark_metrics -v
if ($LASTEXITCODE -eq 0) { throw 'Expected metric module tests to fail before implementation' }
```

- [ ] **Step 5: Implement scalar metrics and canonical aggregation**

Clamp reference/estimate to `[0,1]`; call existing `calc_psnr`, `calc_ssim`, and one injected/reused Alex `LPIPS` instance. Convert only singleton tensor results with `.detach().cpu().item()`. Aggregate in sorted `(step2_seed, source_id)` order with `statistics.fmean`, `statistics.pstdev`, `statistics.median`, `min`, and `max`; serialize using `sort_keys=True`, `allow_nan=False`, UTF-8, newline terminator.

- [ ] **Step 6: Implement read-only kernel analyzer**

The script accepts exact `--snapshot`, `--snapshot-sha256`, `--expected-global-step`, `--kernel-gt`, `--kernel-gt-sha256`, and a new `--output`. It refuses an existing output, verifies file names and hashes, temporarily adds the repository root to `sys.path` only around `pickle.load`, requires snapshot internal `global_step=N+1` and `kernel_nn`, calls `kernel_nn.get_kernel(None, None)`, computes Task 5 metrics, and writes hashes/shapes/alignment rule/metrics.

- [ ] **Step 7: Implement cross-seed aggregator**

The script takes six explicit summary paths, verifies one oracle plus seeds 0–4, recomputes each JSONL hash/count, and writes a new `final-summary.json` containing input/oracle totals, per-seed learned totals, across-seed mean/std of each dataset mean, and kernel PSNR/NCC. It never selects the best seed as the headline result.

- [ ] **Step 8: Update `DeepInvLoss.compute_img_metrics` to the shared scalar API**

Keep one `LPIPS(net_type="alex")` instance and return `dict[str,float]`; `val_loss_with_output` retains reprojection metrics and prefixes image metrics exactly as before so old tests remain valid.

- [ ] **Step 9: Run focused and old no-reference tests**

```powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest tests.test_benchmark_metrics tests.test_deepinv_no_reference -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

### Task 6: Integrate synthetic recording without changing the real output manifest

**Files:**
- Modify: `ddm4ip/trainers/deepinv_denoiser.py:32-54,253-323`
- Create: `tests/test_bdd100k_synthetic_trainer.py`
- Extend: `tests/test_deepinv_no_reference.py`
- Extend: `tests/test_step3_geometry_provenance.py`

**Interfaces:**
- Consumes `cfg.evaluation` fields `quantitative`, `variant`, `step2_seed`, `expected_records`, `kernel_gt_path`, `kernel_gt_sha256`, `pairs_manifest_sha256`.
- Produces `plots/manifest.jsonl`, `plots/metrics.jsonl`, `plots/summary.json`, one `prediction-{source_id}.png`, and one `kernel-{source_id}.pt` per row.

- [ ] **Step 1: Write failing trainer record test**

Build one collated manifest-paired `Batch`, fake identity solver output, true/estimated kernels, and `evaluation.variant="oracle"`. Assert one output-manifest row and one metric row contain source ID, clean/noisy/prediction paths and SHA-256, kernel hashes, input and oracle metrics, sizes, solver config hash, and `step2_seed=null`.

- [ ] **Step 2: Write failing learned-seed and no-overwrite tests**

For `variant="learned"`, require `step2_seed` in `{0,1,2,3,4}` and record it. Run the same sample twice and assert the second call fails before any file/hash changes. Also fail when `kernel_gt_sha256`, pair-manifest hash, source file hash, expected count, or output basename disagrees.

- [ ] **Step 3: Add old-route protection assertions**

Extend existing tests to confirm `step3_bdd100k` still writes its schema-version-1 real `manifest.jsonl`, still omits PSNR/SSIM/LPIPS for `clean=None`, and never creates `metrics.jsonl` or `summary.json` unless `evaluation.quantitative=true`.

- [ ] **Step 4: Run focused tests and verify red**

```powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest tests.test_bdd100k_synthetic_trainer tests.test_deepinv_no_reference tests.test_step3_geometry_provenance -v
if ($LASTEXITCODE -eq 0) { throw 'Expected synthetic trainer tests to fail before integration' }
```

- [ ] **Step 5: Initialize recorder only for explicit quantitative configs**

In `init_datasets`, keep `is_paired=True`. In `init_loss`, after creating `DeepInvLoss`, validate `cfg.evaluation` and create `BenchmarkMetricWriter` only when `quantitative` is true. Compute solver-config SHA from the canonical resolved `models.deepinv_solver` plus `loss` mapping.

- [ ] **Step 6: Add an isolated quantitative branch to `validate_batch`**

Call `val_loss_with_output` once. Before writes, construct and JSON-serialize the output manifest row and metric row. Verify all destination basenames are new; save prediction and filter tensor; append both rows; rewrite deterministic summary from all committed metric rows. Use `prediction-{source_id}.png` and `kernel-{source_id}.pt`. Preserve the existing lines 263–323 branch byte-for-byte for non-quantitative runs.

- [ ] **Step 7: Run focused tests**

```powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest tests.test_bdd100k_synthetic_trainer tests.test_deepinv_no_reference tests.test_step3_geometry_provenance -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

- [ ] **Step 8: Review gate**

Confirm Oracle and learned configs cannot select separate solver settings, real noisy-only metrics remain absent, and a failed sample is not skipped or replaced.

### Task 7: Add isolated synthetic Hydra configurations

**Files:**
- Create: `ddm4ip/configs/paths/bdd100k_synthetic_runtime.yaml`
- Create: `ddm4ip/configs/dataset/bdd100k_synthetic_noisy.yaml`
- Create: `ddm4ip/configs/dataset/bdd100k_synthetic_clean.yaml`
- Create: `ddm4ip/configs/dataset/bdd100k_synthetic_paired.yaml`
- Create: `ddm4ip/configs/models/dpir_bdd100k_256.yaml`
- Create: four synthetic experiment YAML files listed in the file map
- Create: `tests/test_bdd100k_synthetic_configs.py`
- Extend: `tests/test_bdd100k_configs.py`

**Interfaces:**
- Produces four actual module-entry configurations; checkpoint fields remain null until runner injection.

- [ ] **Step 1: Write failing four-config composition tests**

Compose with `paths=bdd100k_synthetic_runtime`, resolve, and assert:

```python
self.assertEqual(step1.dataset.train.name, "patch")
self.assertFalse(step1.dataset.train.need_clean)
self.assertTrue(step1.dataset.train.need_noisy)
self.assertEqual(step1.training.max_steps, 5 * 2**20)

self.assertTrue(step2.dataset.train.need_clean)
self.assertFalse(step2.dataset.train.need_noisy)
self.assertEqual(step2.dataset.train.noise_level_override, 0.02)
self.assertEqual(step2.training.max_val_batches, 0)
self.assertIsNone(step2.models.pretrained_flow.path)

self.assertEqual(oracle.dataset.test.name, "manifest_paired")
self.assertIsNone(oracle.models.kernel.path)
self.assertEqual(oracle.evaluation.variant, "oracle")
self.assertEqual(learned.evaluation.variant, "learned")
self.assertIsNone(learned.models.kernel.path)
self.assertEqual(OmegaConf.to_container(oracle.models.deepinv_solver),
                 OmegaConf.to_container(learned.models.deepinv_solver))
```

Assert both Step 3 configs use `batch_size=1`, `train=false`, `save_eval_to_file=true`, `save_pred_only=true`, `require_output_manifest=true`, full 500-row manifest, and the same loss config.

- [ ] **Step 2: Run test and verify red**

```powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest tests.test_bdd100k_synthetic_configs -v
if ($LASTEXITCODE -eq 0) { throw 'Expected missing synthetic configs before creation' }
```

- [ ] **Step 3: Create paths and dataset configs**

Use exactly:

```yaml
# paths/bdd100k_synthetic_runtime.yaml
data: D:/DDM4IP-runtime/synthetic-benchmarks/bdd100k-motionblur-v1
out_path: D:/DDM4IP-runtime/experiments/bdd100k-synthetic-motionblur-v1
```

Step 1 points both train/test to `${paths.data}/step1-observation/noisy`, uses `patch_size=256`, `need_clean=false`, `need_noisy=true`, no degradation/no noise, no flip. Step 2 points both to `${paths.data}/step2-clean/clean`, uses `patch_size=256`, `need_clean=true`, `need_noisy=false`, `noise_level_override=0.02`, no degradation/no noise, no flip. Step 3 uses `${paths.data}/test-paired/pairs.jsonl`, `name=manifest_paired`, `file_blur`, Gaussian `std=0.02`, and no transforms.

- [ ] **Step 4: Create Step 1 and Step 2 configs from official FFHQ budgets**

Step 1: `xxxs_flow_256`, `lr=0.01`, `batch_size=32`, `n_accum_steps=8`, `max_steps=5Mi`, `save=2Mi`, `plot=128Ki`, `report=16Ki`, `num_workers=4`, `max_val_batches=0`.

Step 2: `xxxs_flow_256`, `direct_kernel`, `kernel_size=28`, `padding=replicate`, `sum_to_one=true`, `learn_output_noise=false`, pretrained path null, official FFHQ `lr`, regularizers, `batch_size=32`, `max_steps=1030Ki`, `save=256Ki`, `plot=128Ki`, `report=16Ki`, `num_workers=4`, `max_val_batches=0`.

- [ ] **Step 5: Create one shared DPIR model config and two Step 3 configs**

`dpir_bdd100k_256.yaml` contains `method: dpir`, `prior: DRUNet`. Both Step 3 configs import it, set `loss.crop_filters=1`, `loss.patch_size=null`, and the exact evaluation contract. Oracle leaves kernel snapshot null so trainer copies the dataset’s frozen file Blur; learned leaves its snapshot path null for runner injection.

- [ ] **Step 6: Run composition tests and actual entry resolution only**

```powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest tests.test_bdd100k_synthetic_configs tests.test_bdd100k_configs -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
foreach ($exp in @('step1_bdd100k_synthetic','step2_bdd100k_synthetic','step3_bdd100k_oracle','step3_bdd100k_synthetic')) {
  & 'E:\Anaconda3\envs\ddm4ip\python.exe' -m ddm4ip.main "exp=$exp" paths=bdd100k_synthetic_runtime --cfg job --resolve
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
```

Expected: four exit codes 0; no dataset construction, download, GPU solver, training, or evaluation.

### Task 8: Create and validate an isolated synthetic scheduled-task runner

**Files:**
- Create: `scripts/bdd100k_synthetic_runner.py`
- Create runtime: three files listed under “Runtime-only files”
- Create: `tests/test_bdd100k_synthetic_runner.py`

**Interfaces:**
- Runner actions: `prepare`, `execute`, `dispatch-failed`; no `direct` action.
- Stages: `inventory`, `build`, `oracle`, `step1`, `step2`, `step3`; modes: `audit`, `pilot`, `full`.
- Fixed Step 2 seeds: 0–4. Step 3 variants: `oracle` or `learned`.

- [ ] **Step 1: Write failing schema and runner validation tests**

Import `scripts.bdd100k_synthetic_runner`. Assert rejection of unknown fields, wrong host/Python, path traversal, reparse point, existing run root, existing benchmark root, arbitrary Hydra override, wrong benchmark hash, Step 2 without Step 1 predecessor, learned Step 3 without same-seed Step 2 predecessor, oracle with a predecessor, seed outside 0–4, and execution without a reserved spec and matching runner SHA.

- [ ] **Step 2: Write failing command-selection tests**

Assert exact mapping:

```python
{"step1": "exp=step1_bdd100k_synthetic",
 "step2": "exp=step2_bdd100k_synthetic",
 "oracle": "exp=step3_bdd100k_oracle",
 "step3:oracle": "exp=step3_bdd100k_oracle",
 "step3:learned": "exp=step3_bdd100k_synthetic"}
```

Step 2 injects the verified `.pt`; learned Step 3 injects the same-seed verified `.pkl`; Oracle injects neither. Every downstream command includes the benchmark summary, pairs manifest, and true-kernel claimed hashes for verification before module execution.

- [ ] **Step 3: Write failing artifact-verification tests**

Use serialization fixtures only. Require Step 1/2 terminal `.pt` internal `N`, `.pkl` internal `N+1`, matching filename N and required model key. Require Oracle/Step 3 `manifest.jsonl`, `metrics.jsonl`, and `summary.json` to contain exactly `expected_manifest_records`, finite metrics, unique source IDs, correct output hashes, and exact solver/benchmark/kernel hashes. Oracle additionally requires mean PSNR/SSIM above input and LPIPS below input; learned has no improvement threshold.

- [ ] **Step 4: Run test and verify red**

```powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest tests.test_bdd100k_synthetic_runner -v
if ($LASTEXITCODE -eq 0) { throw 'Expected runner tests to fail before creation' }
```

- [ ] **Step 5: Implement runner by preserving old fail-closed mechanics**

Copy the proven state/history/log/environment/checkpoint-import pattern into `scripts/bdd100k_synthetic_runner.py`, but do not modify `D:\DDM4IP-runtime\orchestration\bdd100k_runner.py`. Restrict `run_root` to a new descendant of `D:\DDM4IP-runtime\experiments`; write new `spec.json`, `environment.json`, `command.json/txt`, `resolved-config.yaml` for Hydra stages, `status-history.jsonl`, atomic `status.json`, append-only `task.log`, `artifacts.json`, and one `execution.claim`. During `prepare`, record the versioned runner file SHA-256 in the reserved spec; during `execute`, reject execution if the current runner SHA differs.

The allowlisted numeric Hydra overrides are only `training.seed`, batch/budget/report/plot/save/workers/max-val fields, `loss.n_accum_steps`, and `dataset.test.max_imgs`. All artifact paths are absolute regular files under the fixed benchmark/experiment roots with no reparse points.

- [ ] **Step 6: Implement separate PowerShell wrappers**

Both scripts verify hostname, use the fixed Python, invoke `D:\Unsupervised Imaging Inverse Problems\scripts\bdd100k_synthetic_runner.py`, set all process-local runtime/cache variables and offline flags, capture `$LASTEXITCODE` under temporary `$ErrorActionPreference='Continue'`, and refuse an existing Scheduled Task name. `prepare` reserves metadata only; only `start_bdd100k_synthetic_task.ps1` registers and starts pilot/full/audit work.

- [ ] **Step 7: Run parser and runner tests**

```powershell
$errors=$null
[System.Management.Automation.Language.Parser]::ParseFile('D:\DDM4IP-runtime\orchestration\run_bdd100k_synthetic_stage.ps1',[ref]$null,[ref]$errors) | Out-Null
if ($errors.Count) { $errors; exit 1 }
[System.Management.Automation.Language.Parser]::ParseFile('D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1',[ref]$null,[ref]$errors) | Out-Null
if ($errors.Count) { $errors; exit 1 }
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest tests.test_bdd100k_synthetic_runner -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

- [ ] **Step 8: Run the complete no-training regression gate**

```powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

Then rerun the four `--cfg job --resolve` commands from Task 7. Confirm no scheduled task was created, no fixed benchmark/experiment root was created, no pretrained download occurred, and old real BDD100K tests still pass. This ends the separately authorized “code and no-training tests” stage.

### Task 9: Freeze the real source inventory and build the benchmark

**Authorization gate:** Start only in a new conversation that explicitly authorizes synthetic data inventory/build. This task performs data processing and Scheduled Task creation.

**Files produced:**
- Runtime audit: `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-inventory`
- Benchmark: `D:\DDM4IP-runtime\synthetic-benchmarks\bdd100k-motionblur-v1`

- [ ] **Step 1: Re-run startup and no-training gates**

Verify host, Git state, missing remote WORKLOG risk, complete unit tests, four config resolutions, source view counts 1,565/174, and view manifest SHA `6BA1F476AFAEFACA60A9B6EDFB7DB2740BF99D355C12F49335FFB6C342724886`.

- [ ] **Step 2: Schedule inventory-only audit**

Create a frozen `inventory` spec with task name `DDM4IP-BDD100K-SYNTH-Inventory-v1`, run root `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-inventory`, expected source count 1739, and the full verified view-manifest hash. Start it only through `start_bdd100k_synthetic_task.ps1`.

Confirm once with:

```powershell
Get-ScheduledTask -TaskName 'DDM4IP-BDD100K-SYNTH-Inventory-v1' | Get-ScheduledTaskInfo
Get-Content -Raw -LiteralPath 'D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-inventory\status.json'
Get-Content -LiteralPath 'D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-inventory\task.log' -Tail 50
```

Provide the same log command with `-Wait`; `Ctrl+C` stops following only.

- [ ] **Step 3: Independently verify and explicitly freeze inventory hash**

After user reports completion, use a new SSH process to require SUCCESS/exit 0, 1,739 unique IDs/SHA values, 1,565/174 source roots, all 1280×720 RGB, and recompute the candidate manifest SHA. Report that exact digest and stop for the user’s explicit approval before image generation.

- [ ] **Step 4: Build from the approved inventory**

Construct the build spec programmatically from the verified inventory JSON so no digest is manually transcribed:

```powershell
$audit = Get-Content -Raw -LiteralPath 'D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-inventory\artifacts.json' | ConvertFrom-Json
$audit.source_manifest.sha256
```

The build spec fixes task `DDM4IP-BDD100K-SYNTH-Build-v1`, run root `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-build`, benchmark destination, view-manifest hash, and `$audit.source_manifest.sha256`. Start via the synthetic launcher and confirm once.

- [ ] **Step 5: Independently accept the built data**

In a new SSH command, require SUCCESS/exit 0; role counts 1000/100/500/139; PNG counts; all output 256×256 RGB; pair IDs/hashes/noise seeds; zero cross-role ID/SHA overlap; finite normalized 32×32 kernel; repeated sample degradation pixel equality; benchmark summary/source/split/pairs/kernel hashes; and D-drive-only paths. A runner SUCCESS alone is insufficient.

### Task 10: Pass the Oracle GPU pilot gate

**Authorization gate:** New conversation explicitly authorizing only Oracle GPU pilot. Pretrained weight download, if required, needs separate authorization and must finish before this pilot.

- [ ] **Step 1: Verify offline prior readiness**

With `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`, verify DRUNet/DPIR construction uses files already under `D:\DDM4IP-runtime\torch-home`/`xdg-cache`; if it attempts network access or a weight is absent, stop without launching the pilot.

- [ ] **Step 2: Launch fixed 16-sample dev Oracle**

Use task `DDM4IP-BDD100K-SYNTH-Oracle-Pilot-v1`, new run root `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot`, `stage=oracle`, `mode=pilot`, `variant=oracle`, `dataset.test.max_imgs=16`, and `expected_manifest_records=16`. Freeze benchmark summary, dev pairs, and true-kernel SHA in the spec.

- [ ] **Step 3: Confirm once and hand off monitoring**

Provide `Get-Content -Raw -LiteralPath 'D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot\status.json'` and `Get-Content -LiteralPath 'D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot\task.log' -Tail 50 -Wait`; do not wait in the conversation.

- [ ] **Step 4: Independently verify gate conditions**

Require 16 unique rows/files, finite metrics, matching dimensions/hashes, and aggregate Oracle PSNR/SSIM improvement plus LPIPS decrease versus input. If any direction fails, stop before Step 1 training.

### Task 11: Run Step 1 pilot, then full official-budget training

**Authorization gate:** Pilot and full are separate new conversations and separate approvals.

- [ ] **Step 1: Run official-batch feasibility pilots without changing the model/data contract**

Run new pilot specs in this exact order: `(batch, max_steps, suffix) = (1,512,b01), (2,1024,b02), (4,2048,b04), (8,4096,b08), (16,8192,b16), (32,16384,b32)`, each with `n_accum_steps=8` for 64 optimizer updates. For each tuple, derive the exact task and root as `f"DDM4IP-BDD100K-SYNTH-Step1-Pilot-{suffix}"` and `Path(r"D:\DDM4IP-runtime\experiments") / f"bdd100k-synthetic-motionblur-v1-step1-pilot-{suffix}"`. Stop after each scheduled run for independent verification. The required admission result is batch 32 below the agreed memory ceiling and with finite loss/checkpoint output; otherwise return for an explicit batch/accumulation design decision.

- [ ] **Step 2: Launch full Step 1 only after batch-32 admission**

Freeze official `batch_size=32`, `n_accum_steps=8`, `max_steps=5242880`, `save_every_steps=2097152`, `plot_every_steps=131072`, `report_every_steps=16384`, final expected global step 5242880. Use task `DDM4IP-BDD100K-SYNTH-Step1-Full-v1` and run root `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-full`.

- [ ] **Step 3: Independently verify terminal pair**

Require `training-state-5242880.pt` internal step 5242880 and sibling `network-snapshot-5242880.pkl` internal step 5242881, both with `flow_nn`, plus SHA-256, resolved config, completion marker, exit 0, and benchmark contract. Do not authorize Step 2 from an earlier periodic file.

### Task 12: Run one Step 2 pilot, then five full seeds

**Authorization gate:** One-seed pilot and five-seed full execution are separate approvals.

- [ ] **Step 1: Prove clean-only Step 2 at seed 0**

Use only the verified Step 1 `.pt`, seed 0, official batch 32, 64 updates (`max_steps=2048`), `max_val_batches=0`, task `DDM4IP-BDD100K-SYNTH-Step2-Pilot-seed0`, run root `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step2-pilot-seed0`, and no `kernel_gt` path in the Hydra command/config. Verify the dataset reads only the 100 Step 2 clean images and output contains a terminal kernel snapshot.

- [ ] **Step 2: Launch five independent full runs**

For each `seed in range(5)`, derive the exact task and root as `f"DDM4IP-BDD100K-SYNTH-Step2-Full-seed{seed}"` and `Path(r"D:\DDM4IP-runtime\experiments") / f"bdd100k-synthetic-motionblur-v1-step2-full-seed{seed}"`. Use the same verified Step 1 checkpoint/hash and official `batch_size=32`, `max_steps=1054720`, `save_every_steps=262144`, `plot_every_steps=131072`, `report_every_steps=16384`. Do not run multiple seeds in one mutable output directory.

- [ ] **Step 3: Independently verify every seed**

For each seed require `.pt` internal 1054720, `.pkl` internal 1054721, `kernel_nn`, SHA-256, exit 0 and exact seed/config. Run `analyze_bdd100k_synthetic_kernel.py` read-only against each verified snapshot and frozen kernel; preserve all five kernel PSNR/NCC results without selecting or discarding seeds.

### Task 13: Run formal 500-image Oracle and five learned evaluations

**Authorization gate:** New conversation explicitly authorizing Step 3 formal evaluation. The 500-image test set must not have been used for tuning.

- [ ] **Step 1: Run full Oracle first**

Use task `DDM4IP-BDD100K-SYNTH-Step3-Oracle-Full-v1`, run root `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step3-oracle-full`, `step3_bdd100k_oracle`, exactly 500 test rows, batch size 1, frozen DPIR config, and no Step 2 predecessor. Require input/oracle metrics, files, hashes, source-set hash and Oracle improvement directions before learned runs.

- [ ] **Step 2: Run learned evaluation for seeds 0–4**

For each `seed in range(5)`, derive the exact task and root as `f"DDM4IP-BDD100K-SYNTH-Step3-Learned-seed{seed}"` and `Path(r"D:\DDM4IP-runtime\experiments") / f"bdd100k-synthetic-motionblur-v1-step3-learned-seed{seed}"`. Each spec injects only that seed’s independently verified `.pkl`; benchmark input, pairs, kernel truth, solver config, batch size and metrics implementation remain identical to Oracle. Require exactly 500 rows for every seed. A learned run is valid even if it does not improve input, provided all contracts and metrics are valid.

- [ ] **Step 3: Independently verify six result sets**

Recompute file SHA-256, every row’s three image metrics, kernel metrics, summary statistics, source ID set, and failure count. Confirm Oracle/learned solver config hashes match and only kernel hashes differ.

### Task 14: Aggregate, review failures, and report bounded conclusions

**Authorization gate:** New result-review conversation after all six formal evaluations finish.

- [ ] **Step 1: Run the deterministic aggregator into a new result directory**

Pass the one Oracle and five learned summary paths explicitly to `aggregate_bdd100k_synthetic_results.py`; write only to new `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-results\final-summary.json`, require source-set, pair-manifest, true-kernel and solver hashes to match, and refuse an existing result root or final summary.

- [ ] **Step 2: Independently recompute a fixed audit sample**

Select sample IDs before viewing results by sorting SHA-256 of `bdd100k-motionblur-v1\0source_id` and taking the first 25. Recompute PSNR/SSIM/LPIPS from PNGs and compare to JSONL within numeric tolerance; inspect all failures rather than deleting them.

- [ ] **Step 3: Write the final bounded report**

Report input, Oracle, each learned seed, across-seed mean/std, kernel PSNR/NCC, failure count, runtime/hardware, fixed-noise implementation difference, lack of source-group IDs, and central-crop limitation. Separate conclusions for execution success, Oracle validity, kernel accuracy, and restoration improvement. State explicitly that this is a BDD100K-domain synthetic known-degradation reproduction, not FFHQ Table 2 reproduction, and do not use 28.8 dB/0.069 as a pass threshold.

## Final Self-Review Checklist

- [ ] Every design requirement maps to Tasks 1–14; no code/data/run phase is implicitly authorized by this document.
- [ ] Source inventory is frozen and user-approved before derived pixels are written.
- [ ] Step 1 has no clean tensor; Step 2 has no noisy/test tensor and no `k_gt`; Step 3 pairs only through manifest.
- [ ] The same frozen kernel produces Step 1/test/dev observations and Oracle physics.
- [ ] Oracle and learned use the same solver configuration hash.
- [ ] Exactly five Step 2 seeds are preserved unless the user explicitly approves a documented deviation.
- [ ] Old real BDD100K configs/tests/output manifest continue to pass and never emit pseudo-reference metrics.
- [ ] All targets are fail-closed and non-overwriting; no bulk delete appears in commands.
- [ ] All long operations use Scheduled Tasks with `RUNNING/SUCCESS/FAILED`, append-only logs, frozen command/config, and independent post-run verification.
- [ ] Remote Git remains read-only and the missing remote WORKLOG risk remains visible until the user resolves it.

## Execution Handoff

Plan implementation must begin in a new conversation with explicit authorization limited to **Tasks 1–8: code and no-training tests**. At that time use `superpowers:subagent-driven-development` or `superpowers:executing-plans`, re-run the full startup verification, and stop after the complete no-training regression gate. Tasks 9–14 require their own later approvals exactly as marked.
