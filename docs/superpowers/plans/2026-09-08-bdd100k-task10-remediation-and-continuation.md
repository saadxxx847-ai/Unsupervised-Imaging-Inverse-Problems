# BDD100K Task 10 前置修正与后续执行总计划

> **最新状态（2026-09-19，优先于下文较早的当前总状态）：** Step1 full b16 async 在本轮唯一检查时仍运行；本次全项目审查已在独立副本修复27类问题，114项验收中109通过、5项GPU跳过。补丁尚未部署，现有训练未被干预。下一步仍是新对话授权full终态独立验收；部署、Step2/3与评估各需另行授权。详见本文末尾的2026-09-19全项目审查交接及审查根 audit-report.md。较早b32/full未准入文字仅保留历史语境。


> **给后续执行者：** 必须逐项执行本计划，并使用 `executing-plans`、`test-driven-development`、`systematic-debugging` 和 `verification-before-completion`。项目规则禁止默认启用多代理；除非用户在确确授权，否则不得派生子代理。所有复选框都是状态记录，不构成训练、下载、评估或计划任务授权。

**目标：** 修复 Task 10 Oracle 前置代码、synthetic runner、指标工件和计划任务 wrapper 的已确认缺陷；完成无训练验收后，按独立授权依次通过 AlexNet 权重门、Task 10 Oracle 16 图门，再进入 Task 11。

**架构：** 保留现有 synthetic benchmark、真实 BDD100K 主线和历史运行证据。定量输出统一落在每个 reserved run root 的 `plots` 子目录，runner 在子进程前验证输入哈希、在子进程后验证评估或 checkpoint 工件，wrapper 只触发一次。所有修复测试先行；真正的下载、GPU Oracle、pilot 和训练继续分阶段授权。

**技术栈：** Python 3.10；PyTorch 2.4.1+cu118；DeepInv 0.4.2；Hydra/OmegaConf；PowerShell 5.1；Windows Task Scheduler；`unittest`。

**批准设计：** `docs/superpowers/specs/2026-09-06-bdd100k-known-blur-quantitative-reproduction-design.md`

**原实施计划：** `docs/superpowers/plans/2026-09-06-bdd100k-known-blur-quantitative-reproduction.md`

**本文性质：** 原计划 Task 10—14 的勘误、修正和跨对话执行手册；不替代批准设计，也不改变数据划分、退化定义、训练预算或阶段授权边界。

## 1. 每个新对话必须先做什么

用户在新对话中附上本文，并明确“已完成到哪一项”和“本对话授权哪一阶段”。执行者仍必须：

- [ ] 完整读取本机控制目录 `D:\Unsupervised Imaging Inverse Problems\WORKLOG.md`。
- [ ] 通过 `ssh group-pc` 核验 `hostname` 精确为 `DESKTOP-KBM1345`。
- [ ] 在远端 `D:\Unsupervised Imaging Inverse Problems` 执行只读 `git status`，保留全部既有修改。
- [ ] 完整读取远端 `WORKLOG.md`；与本机不一致时，以远端较新事实为准并报告差异。
- [ ] 完整读取上述批准设计、原实施计划和本文，不凭聊天摘要猜测状态。
- [ ] 新鲜核验上一阶段的准入证据；复选框和旧日志都不能替代实际验证。
- [ ] 严格遵守本轮用户授权；本文自身不授权下载、创建计划任务、GPU 推理、训练或正式评估。

推荐的新对话开头：

```text
请先按 AGENTS.md 完成完整启动核验，并完整读取已批准设计、原实施计划和我附上的《BDD100K Task 10 前置修正与后续执行总计划》。
我确认已完成到：<填写本文中的阶段和检查项>。
本对话只授权：<填写一个明确阶段>。
除该阶段外，不授权下载权重、创建或启动其他计划任务、Oracle、训练、正式评估或删除历史证据。
```

## 2. 2026-09-08 已核验基线

这些是编写本文时的事实，后续仍需新鲜复核：

- [x] Task 9 benchmark 数据与 provenance audit 已独立验收；benchmark 根为 `D:\DDM4IP-runtime\synthetic-benchmarks\bdd100k-motionblur-v1`。
- [x] 角色计数为 `1000/100/500/139`；test pairs SHA-256 为 `3C86E1B8CC419E6FDB627EB60D7C6DD209015123EEC44F790D0115B39BFFF9E4`，dev pairs SHA-256 为 `482277FD47D395B369A5C0E53E3BB7D7006133F8D819DE0501E878E6F8395530`。
- [x] benchmark summary SHA-256 为 `97F874E8497F4F8FB2C814B814C15E3C43CC736AFC344DF449E58C99D58A346E`。
- [x] 真核文件 SHA-256 为 `4E292CA42C026965EF9B6D16CACEC83091DFC2E461C2C6788C6FDC690F832A7A`，形状 `1×1×32×32`，有限、非负、归一化。
- [x] DRUNet 权重位于 `D:\DDM4IP-runtime\torch-home\hub\checkpoints\drunet_deepinv_color_finetune_22k.pth`，大小 `130585443` 字节，SHA-256 为 `20296845D272D3D786B89EA3C1208D5F2CEB57658A499D4DD28073CBB73508AA`；DRUNet/DPIR 离线构造已通过。
- [x] 最新完整无训练测试为 `69/69`、退出码 `0`，paired metadata 聚焦回归为 `35/35`、退出码 `0`，四个 synthetic Hydra 配置解析均退出码 `0`；严格离线三模型构造通过且 network guard hits=`0`。
- [x] Task 10 Oracle pilot 已完成；v6 Scheduled Task 独立验收为 SUCCESS，16 图工件、SHA 链、有限/归一化 kernel 和三项 Oracle 改善方向全部通过。
- [x] LPIPS 所需 AlexNet 主干 `alexnet-owt-7be5be79.pth` 已在规范 D 盘缓存中验收；离线 LPIPS/DRUNet/DPIR 构造通过且 network guard hits 为 `0`。
- [x] Task 11 Step 1 pilots 已准入并已完成 b01、b02、b04 的独立终态验收；Step 1 full 尚未准入。

当前总状态：Phase A、Phase B、Phase C / Task 10 Oracle GPU pilot 已完成并独立关闭；Phase D / Task 11 Step 1 的 b01、b02、b04、b08、b16 已通过独立终态验收，v1-v5 失败证据、v6 成功证据以及 b01/b02/b04/b08/b16 证据均保留。NEXT = Phase D：等待用户在新对话中明确授权 b32 pilot；不自动进入 Step 1 full training。

> **状态解释：** 本计划中较早日期的失败段落和未勾选项只保留当时的诊断事实；当前状态以本节、v6 最终成功证据和“最终完成定义”为准，不得将历史未勾选项解释为当前 Phase C 未关闭。

## 3. 已确认问题与解决方向

| 编号 | 阻塞 | 直接后果 | 修复归属 |
| --- | --- | --- | --- |
| P0 | `stage=oracle` 不允许 `variant=oracle`，且 Oracle 未注入完整 evaluation 字段 | 精确 dry-run 得到 dev 16 图却仍要求 500 条，并留下空核/清单哈希 | A1 |
| P1 | paired 数据集 Gaussian 默认 `std=0.04` | DPIR 使用错误噪声水平；批准设计要求 `0.02` | A1 |
| P2 | writer 每处理一图就强制要求全部记录已齐 | 16 图 pilot 在第 1 图后失败 | A2 |
| P3 | trainer 写 `<run_root>\plots`，runner 验收 `<run_root>`；schema 互不兼容 | 即使模型运行成功，工件验收也必然失败 | A2、A3 |
| P4 | manifest 缺 `prediction_sha256`，summary 不含 input 汇总和完整哈希链 | 无法验证预测文件、Oracle 改善方向和来源一致性 | A2 |
| P5 | runner execute 不做输入预检，也不调用评估/checkpoint 后验 | 子进程退出码 0 会被误写为整体成功 | A3 |
| P6 | reserved `run_root` 未绑定 Hydra 输出，子进程输出仍落固定目录 | pilot/full 相互碰撞，runner 状态与模型工件分离 | A3 |
| P7 | 子进程 stdout/stderr 未追加到 `task.log` | 真实 traceback 可能丢失 | A3 |
| P8 | Step 2/learned Step 3 未解析 predecessor，也未注入 checkpoint | 后续训练/评估启动即失败或误用产物 | A4 |
| P9 | Step 1 snapshot 被错误要求 `kernel_nn`；仓库外 pickle 导入路径不稳 | 真实 checkpoint 无法通过验收 | A4 |
| P10 | launcher 同时设置一分钟触发器并立即启动 | 同一个任务执行两次，第二次伪造 `LastTaskResult=1` | A5 |
| P11 | runtime wrapper 使用 `torch-cache`，规范权重在 `torch-home` | 离线权重来源不一致 | A5 |
| P12 | 指标按保存前浮点预测计算，Task 14 又从 8-bit PNG 复算 | 正式复核可能产生系统性差异 | A2、A6 |
| P13 | aggregator 不复核 JSONL、不算五 seed 的跨 seed mean/std、不含核指标 | Task 14 无法按批准设计完成 | A6 |
| P14 | AlexNet 主干权重缺失 | Task 10 可能偷偷访问网络 | B |

## 4. 文件责任图

### 仓库内修改

- `scripts/bdd100k_synthetic_runner.py`：Oracle 契约、输入预检、run-root 绑定、真实 execute、日志、后验验收、predecessor/checkpoint 注入。
- `ddm4ip/configs/dataset/bdd100k_synthetic_paired.yaml`：冻结 `noise.std=0.02`。
- `ddm4ip/trainers/deepinv_denoiser.py`：16 图写出生命周期、PNG 后指标、manifest/hash 链。
- `ddm4ip/utils/benchmark_metrics.py`：统一记录/summary schema、多图 finalize、JSONL 复核、跨 seed 汇总。
- `scripts/aggregate_bdd100k_synthetic_results.py`：接受并核验一个 Oracle、五个 learned 和五个 kernel 分析结果。
- `tests/test_bdd100k_synthetic_runner.py`：runner 合同、pre/postflight、checkpoint 键和真实 execute 集成回归。
- `tests/test_bdd100k_synthetic_trainer.py`：16 图 writer、PNG 量化后指标、hash/schema 回归。
- `tests/test_benchmark_metrics.py`：summary、JSONL、跨 seed mean/std 和 kernel 结果回归。
- `tests/test_bdd100k_synthetic_configs.py`：噪声、Oracle dev/test 清单和相同 solver 配置回归。
- 必要时新增 `tests/fixtures/synthetic_execute_child.py`：只写确定性夹具工件的无训练子进程，用于真正经过 `subprocess.run` 的 execute 测试；不得导入训练器或触发 GPU。

### 仓库外 runtime 修改

- `D:\DDM4IP-runtime\orchestration\synthetic-step-spec.schema.json`：冻结 predecessor、输入哈希和 evaluation 合同。
- `D:\DDM4IP-runtime\orchestration\run_bdd100k_synthetic_stage.ps1`：统一进程级缓存到 `torch-home`，保持离线标志与追加式日志。
- `D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1`：注册无自动时间触发器的任务，然后仅手动启动一次。

## 5. Phase A：代码与无训练修正

**授权文本：**

```text
本对话只授权执行本文 Phase A：修复 Task 10 前置代码、synthetic runner、wrapper、最终聚合器和无训练回归测试。必须测试先行。不得下载权重、创建或启动计划任务、运行 Oracle、训练、正式评估或数据处理。
```

### A0. 建立修正前证据

- [x] 记录上述仓库内文件和三个 runtime 文件的修改前 SHA-256。
- [x] 新鲜运行完整 `unittest` 与四个 Hydra `--cfg job --resolve`，仅作为基线；旧测试全绿不能取消后续红灯要求。
- [x] 用精确 Oracle pilot spec 运行 dry-run/override 组合，保存修复前证据：`pairs_role=dev_reserve`、`max_imgs=16`，但 `expected_records=500`、核/清单哈希为空且噪声为 `0.04`。
- [x] 确认没有新计划任务、Oracle 根、训练进程或 benchmark 写入。

### A1. 修复 Oracle spec、dry-run 和噪声合同

**先写失败测试：**

- [x] 在 `tests/test_bdd100k_synthetic_runner.py` 增加 `stage=oracle, variant=oracle` 合法测试；Oracle 任何 seed/predecessor、空 variant 或 learned variant 都必须拒绝。
- [x] 断言 `command_for("oracle", "oracle") == "exp=step3_bdd100k_oracle"`。
- [x] 断言 Oracle pilot 同时注入：

```text
dataset.test.pairs_role=dev_reserve
dataset.test.max_imgs=16
evaluation.expected_records=16
evaluation.kernel_gt_path=<benchmark>/degradation/kernel-gt.pt
evaluation.kernel_gt_sha256=<冻结 kernel file SHA>
evaluation.pairs_manifest_sha256=<冻结 dev pairs SHA>
evaluation.benchmark_summary_sha256=<冻结 summary SHA>
```

- [x] 在 `tests/test_bdd100k_synthetic_configs.py` 断言 paired 配置解析后 `dataset.test.noise.std == 0.02`，Oracle/learned solver 配完全相同。
- [x] 运行聚焦测试并确认至少一个新增断言以预期原因失败，记录退出码 `1`；不得用语法错误充当红灯。

**最小实现：**

```python
if stage == "oracle":
    require(variant == "oracle" and seed is None and predecessor is None)
elif stage == "step3":
    require(variant in {"oracle", "learned"})
else:
    require(variant is None)
```

- [x] 将命令映射改为 `("oracle", "oracle")`；evaluation 注入条件改为 `stage in {"oracle", "step3"}`。
- [x] Oracle pilot 从 `dev-reserve/pairs.jsonl` 取 pairs SHA；正式 Oracle/learned 从 `test-paired/pairs.jsonl` 取 pairs SHA。spec 中的相对路径和哈希必须一致，不允许只切换 `pairs_role`。
- [x] 在 `bdd100k_synthetic_paired.yaml` 显式设置 Gaussian `std: 0.02`。
- [x] 重新运行聚焦测试和四配置解析，确认 Oracle dry-run 的 16 图、路径、哈希、噪声全部一致。

### A2. 修复 16 图 writer、统一 schema 和 PNG 指标来源

**先写失败测试：**

- [x] 模拟连续 16 个唯一 source：第 1—15 次只能追加 JSONL，不得写最终 `summary.json` 或抛 expected-count；第 16 次才允许原子写 summary。
- [x] 第 17 条、重复 source、非有限指标、错误 seed、错误输入哈希必须 fail closed。
- [x] manifest 和 metrics 每行都必须包含 `prediction_path`、`prediction_sha256`、`kernel_path`、`kernel_sha256`、`kernel_gt_sha256`、`pairs_manifest_sha256`、`benchmark_summary_sha256`、`solver_config_sha256`。
- [x] summary 必须使用以下单一合同：

```json
{
  "records": 16,
  "failures": 0,
  "source_set_sha256": "<64 hex>",
  "pairs_manifest_sha256": "<64 hex>",
  "benchmark_summary_sha256": "<64 hex>",
  "kernel_gt_sha256": "<64 hex>",
  "solver_config_sha256": "<64 hex>",
  "statistics": {
    "input_psnr": {"mean": 0, "std": 0, "median": 0, "min": 0, "max": 0},
    "input_ssim": {"mean": 0, "std": 0, "median": 0, "min": 0, "max": 0},
    "input_lpips": {"mean": 0, "std": 0, "median": 0, "min": 0, "max": 0},
    "restored_psnr": {"mean": 0, "std": 0, "median": 0, "min": 0, "max": 0},
    "restored_ssim": {"mean": 0, "std": 0, "median": 0, "min": 0, "max": 0},
    "restored_lpips": {"mean": 0, "std": 0, "median": 0, "min": 0, "max": 0}
  },
  "mean": {
    "input_psnr": 0,
    "input_ssim": 0,
    "input_lpips": 0,
    "restored_psnr": 0,
    "restored_ssim": 0,
    "restored_lpips": 0
  },
  "manifest_jsonl_sha256": "<64 hex>",
  "metrics_jsonl_sha256": "<64 hex>"
}
```

- [x] 加入量化一致性测试：保存 prediction PNG，再从 PNG 读取并计算指标；JSONL 中 restored 指标必须与该 PNG 的独立复算一致，而不是与保存前 float tensor 绑定。
- [x] 运行聚焦测试，确认新增测试因第 1 图就 finalize、缺 hash、缺 input 汇总或量化差异而红灯。

**最小实现：**

- [x] `BenchmarkMetricWriter` 接收并保存真实 `pairs_manifest_sha256` 与 `benchmark_summary_sha256`，不再只把 pairs hash 放在 trainer 未使用字段里。
- [x] 将严格 `write_summary()` 改为显式终结合同：`finalize_if_complete()` 在记录不足时返回 `None`，恰好等于 expected count 时写 summary，超过时拒绝；runner 后验仍要求最终 summary 存在。
- [x] trainer 在初始化时实际 SHA-256 校验解析后的 `cfg.dataset.test.path` 和 benchmark summary 文件，再创建 writer。
- [x] 每张 prediction 先写入新文件、计算 SHA、重新加载 PNG，再计算 restored 指标；不得从保存前 float tensor生成正式 restored 指标。
- [x] manifest、metrics 和 summary 使用同一 hash/schema；runner、aggregator 和测试不再各自发明字段名。
- [x] 工件固定落在 `<run_root>\plots`。失败留下的部分工件作为证据保留，不自动删除、不覆盖后重跑。

### A3. 修复 run-root 绑定、输入预检、真实 execute、日志和后验

**先写失败测试：**

- [x] runner 生成的 Hydra 命令必须包含内部生成、用户不可任意覆盖的：

```text
training.log_dir=<run_root parent>
exp_name=<run_root name>
hydra.run.dir=<run_root>
```

- [x] 子进程启动前，分别篡改 summary、当前角色 pairs、kernel 文件一个字节，断言 execute 不调用 child 且写 `FAILED`。
- [x] 子进程退出码 0 但缺 summary、记录少于预期、prediction SHA 错、Oracle 方向错误时，断言最终状态仍为 `FAILED`。
- [x] 增加无训练“真实 execute”集成：prepare 一个临时 spec，patch `stage_command` 只把命令指向 `tests/fixtures/synthetic_execute_child.py`，实际经过 `subprocess.run`；fixture 写完整合法工件后应得到 `SUCCESS`，破坏任一工件应得到 `FAILED`。禁止把单纯 mock `subprocess.run(returncode=0)` 当成此项通过。
- [x] 断言 fixture 子进程 stdout 和 stderr 都出现在根目录 append-only `task.log`。

**最小实现顺序：**

```python
spec = execute_reserved(...)
preflight_benchmark_artifacts(spec)
predecessor = resolve_and_verify_predecessor(spec)
command = stage_command(spec, **predecessor)
run_child_with_combined_append_log(command, run_root / "task.log")
postflight_stage_artifacts(spec, run_root)
record SUCCESS only after postflight
```

- [x] `preflight_benchmark_artifacts()` 对 spec 指定的 summary、当前角色 pairs、kernel 做 regular-file、根目录约束和完整 SHA-256 核验。
- [x] `verify_evaluation_artifacts()` 固定读取 `<run_root>\plots`，验证 manifest/metrics source 集合完全相等、记录恰好 N、所有数值有限、prediction/kernel 文件及 SHA 正确、summary/JSONL SHA 正确；Oracle 额外核验三项改善方向。
- [x] `subprocess.run` 将 stdout/stderr 合并后追加到根 `task.log`，以 `returncode` 判断原生命令成败。
- [x] 任何 preflight、child 或 postflight 异常都追加异常类型/信息并记录 `FAILED/exit_code=1`；只有后验完全通过才写 `SUCCESS`。

### A4. 修复 predecessor、checkpoint 注入和真实模型键

**冻结 predecessor schema：**

```json
{
  "stage": "step1-or-step2",
  "run_root": "D:/DDM4IP-runtime/experiments/<approved-run>",
  "expected_step": 5242880,
  "training_state": "checkpoints/training-state-5242880.pt",
  "training_state_sha256": "<64 hex>",
  "network_snapshot": "checkpoints/network-snapshot-5242880.pkl",
  "network_snapshot_sha256": "<64 hex>",
  "seed": null
}
```

这里的示例数字只对应 Step 1 full；Step 2 使用其批准预算终点。实际 spec 必须由上一阶段独立验收结果程序化生成，不得手抄相似文件名。

**先写失败测试：**

- [x] Step 2 只接受 `stage=step1` 的已核验终点 pair，并注入明确 `.pt` 到 `models.pretrained_flow.path`。
- [x] learned Step 3 只接受同 seed 的 `stage=step2` 终点 pair，并注入明确 `.pkl` 到 `models.kernel.path`。
- [x] 错 stage、错 seed、错文件名、错 SHA、`.pt global_step != N`、`.pkl global_step != N+1`、缺 required model key 都拒绝。
- [x] Step 1 `.pt` 与 `.pkl` 都要求 `flow_nn`；Step 2 `.pt` 与 `.pkl` 都要求 `kernel_nn`。不得再把 Step 1 snapshot 映射为 `kernel_nn`。
- [x] 用一个真实旧 checkpoint 夹具，在“仓库根不在 `sys.path`”条件下验证 `.pt/.pkl`；pickle 期间临时加入仓库根，返回后恢复原 `sys.path`。

**最小实现：**

- [x] 新增 `resolve_and_verify_predecessor(spec)`，核验 schema、根目录、普通文件、文件名、两份 SHA、内部步数和 stage 对应模型键，返回明确 `flow_checkpoint` 或 `kernel_snapshot`。
- [x] `main execute` 必须把该返回值传入 `stage_command()`；不得保留当前不传参数的调用。
- [x] checkpoint 后验也使用同一 stage→model-key 表，避免前序注入与终点验收采用两套规则。

### A5. 修复 wrapper 单次触发和统一缓存

**先写失败测试：**

- [x] 解析 `start_bdd100k_synthetic_task.ps1`，断言不存在 `New-ScheduledTaskTrigger`，`Start-ScheduledTask` 恰好一次，execute 参数指向 `<run_root>\spec.json`。
- [x] 断言 `run_bdd100k_synthetic_stage.ps1` 的 `TORCH_HOME` 精确为 `D:\DDM4IP-runtime\torch-home`，并设置 `HF_HUB_OFFLINE=1`、`TRANSFORMERS_OFFLINE=1`。
- [x] 断言 wrapper 仍以 `$LASTEXITCODE` 判定 Python 成败，PowerShell parser `parse_errors=0`。

**最小实现：**

- [x] 通过 `Register-ScheduledTask` 注册无时间触发器的任务，再只调用一次 `Start-ScheduledTask`；不得同时保留一分钟后自动触发。
- [x] 第二次 launcher 调用因同名 task 或既有 run root 在 prepare 前拒绝，不得改写已有 SUCCESS/FAILED 历史。
- [x] wrapper 统一使用 `torch-home`，不删除当前 `torch-cache` 中的重复 DRUNet 文件。

### A6. 修复最终聚合与 PNG 复算合同

**先写失败测试：**

- [x] aggregator 必须显式接收 1 个 Oracle summary、5 个 learned summary 和 5 个 kernel analysis JSON；缺一个、seed 重复、source set/hash/solver 不一致都拒绝。
- [x] 对每个 summary，从其同目录重新读取 `manifest.jsonl`、`metrics.jsonl`，复算文件 SHA、记录数、source 集合和全部统计；不得只信 summary。
- [x] 对每项 restored PSNR/SSIM/LPIPS，计算五个 seed 的数据集均值之 `statistics.fmean` 与 `statistics.pstdev`；保留每个 seed，不选择最佳 seed 作为 headline。
- [x] final summary 包含 input、Oracle、每 seed learned、跨 seed mean/std、五个 kernel PSNR/NCC、失败数和全部 provenance hash。
- [x] 从 8-bit prediction PNG 独立复算受控样本指标，与 JSONL 在冻结数值容差内一致；由于 A2 已改为 PNG 后计算，容差只覆盖库级浮点舍入。

**最小实现：**

- [x] 扩展 `aggregate_summaries()` 或 CLI 参数，使 kernel 结果成为必需输入。
- [x] 添加 `verify_summary_against_jsonl()`，聚合前逐运行复核，不允许 summary-only 聚合。
- [x] 保持输出目标拒绝覆盖；不得因某 seed 指标差而丢弃。

### A7. Phase A 全量验收门

- [x] 聚焦测试全部通过：

```powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest `
  tests.test_bdd100k_synthetic_configs `
  tests.test_bdd100k_synthetic_trainer `
  tests.test_benchmark_metrics `
  tests.test_bdd100k_synthetic_runner -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

- [x] 完整远端无训练测试通过：

```powershell
& 'E:\Anaconda3\envs\ddm4ip\python.exe' -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

- [x] 四个模块入口配置解析都通过，且 Oracle pilot 解析快照明确为 dev 16 图、`std=0.02`、`expected_records=16` 和完整 hash/path：

```powershell
$exps = @(
  'step1_bdd100k_synthetic',
  'step2_bdd100k_synthetic',
  'step3_bdd100k_oracle',
  'step3_bdd100k_synthetic'
)
foreach ($exp in $exps) {
  & 'E:\Anaconda3\envs\ddm4ip\python.exe' -m ddm4ip.main "exp=$exp" paths=bdd100k_synthetic_runtime --cfg job --resolve
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
```

- [x] 两个 PowerShell wrapper 均 `parse_errors=0`，runtime JSON schema 可解析。
- [x] 无训练真实 execute 的成功和故意失败夹具均符合预期；失败不能被标为 SUCCESS。
- [x] 独立只读确认没有创建新 Scheduled Task、没有 Oracle/训练进程、没有下载权重、没有改写 benchmark 或历史运行根。
- [x] 对所有改动运行限定 `git diff`；真实 BDD100K no-reference 测试继续通过。
- [x] 把红灯、绿灯、完整测试数/退出码、四配置解析、关键文件新 SHA、遗留风险和下一门禁写入远端 `WORKLOG.md`，同时更新本文 Phase A 复选框。

**Phase A 完成只代表：** 代码链已准备进入 AlexNet 权重门。它不代表 Task 10 已完成，也不授权 Task 11。

## 6. Phase B：AlexNet 权重准备与离线总验收

**必须新对话、单独授权。** 推荐授权文本：

```text
本对话只授权执行本文 Phase B：准备 LPIPS AlexNet 主干权重并完成离线总验收。允许创建一个新的权重准备计划任务；不授权 Oracle、训练或正式评估。权重、临时文件、日志和缓存只能落在 D:\DDM4IP-runtime，并保留旧失败证据。
```

- [x] 新鲜核验 C/D/E 剩余空间及进程级 TEMP/TMP/TORCH_HOME/XDG_CACHE_HOME；不得写 C 盘缓存。
- [x] 通过新的、唯一运行根和 Scheduled Task 从 torchvision 官方 URL 获取 `alexnet-owt-7be5be79.pth`；不得覆盖旧失败运行根，也不得把首次下载混入 Oracle。
- [x] 目标固定为 `D:\DDM4IP-runtime\torch-home\hub\checkpoints\alexnet-owt-7be5be79.pth`；记录来源 URL、精确字节数和完整 SHA-256，并二次独立复算。
- [x] 在 `HF_HUB_OFFLINE=1`、`TRANSFORMERS_OFFLINE=1` 下把所有网络下载入口替换为“被调用即失败”的守卫，实际构造：

```text
LPIPS AlexNet
DRUNet(pretrained="download")
DPIR(使用上述 DRUNet)
```

- [x] 三者构造全部通过、无网络调用、缓存均在 `torch-home` 后，才把 Phase B 标为完成。
- [x] 写远端 `WORKLOG.md`：task 名、run root、状态历史、日志、LastTaskResult、两类权重路径/大小/SHA、离线构造退出码和清理清单。

## 7. Phase C：Task 10 Oracle GPU pilot

**必须新对话、单独授权。** 推荐授权文本：

```text
本对话只授权执行本文 Phase C：Task 10 Oracle GPU pilot。不得训练、不得下载权重、不得运行正式 500 图评估。只能使用已独立验收的 benchmark 与离线权重，通过 synthetic launcher 创建并启动一个 16 图 dev_reserve Oracle 计划任务。
```

- [x] 启动前重跑 benchmark summary/dev pairs/kernel 哈希和 LPIPS+DRUNet+DPIR 离线构造门；preflight v5 退出码为 `0`，离线网络守卫命中 `0`。
- [x] spec 固定：`stage=oracle`、`mode=pilot`、`variant=oracle`、无 seed、无 predecessor、`dataset.test.max_imgs=16`、`expected_manifest_records=16`。
- [x] 使用新 task `DDM4IP-BDD100K-SYNTH-Oracle-Pilot-v6` 和新 run root `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot-v6`；v1-v5 失败运行根均保留且未覆盖。
- [x] 启动后独立确认 v6 task、runner/child 进程、status/history/log 和 run root 已创建并开始更新；终态为 `status=SUCCESS`、`exit_code=0`、`LastTaskResult=0`，无重复触发和残留进程。

```powershell
Get-ScheduledTask -TaskName 'DDM4IP-BDD100K-SYNTH-Oracle-Pilot-v3' | Get-ScheduledTaskInfo
Get-Content -Raw -LiteralPath 'D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot-v3\status.json'
Get-Content -LiteralPath 'D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot-v3\task.log' -Tail 50 -Wait
```

- [x] 用户报告结束后，在新的 SSH 命令中独立检查 `status-history.jsonl`、`task.log`、`status.json`、`LastTaskResult`，确认状态历史为 `RESERVED -> RUNNING -> FAILED` 且无重复触发。
- [x] 独立验收 v6 `plots`：16 个唯一 source、16 个 prediction/kernel、manifest/metrics/summary 完整 SHA 链、尺寸一致、全部指标有限、PNG 尺寸与 SHA 复核一致。
- [x] v6 总体方向满足：Oracle PSNR 高于 input、SSIM 高于 input、LPIPS 低于 input；独立审计退出码 `0`。
- [x] 把 v1-v5 失败证据和 v6 成功证据写入远端 `WORKLOG.md` 并更新本文；旧失败项保持历史状态。

**2026-09-08 失败证据（Phase C 未完成）：** v2 launcher 退出码为 `0`，但任务 `LastTaskResult=1`，状态历史严格为 `RESERVED -> RUNNING -> FAILED`；失败发生在 `deepinv_denoiser.py:317` 的 `kernel_gt_sha256` 大小写敏感比较，`plots` 中 prediction/kernel 数量均为 `0` 且没有 `summary.json`。本条不勾选 Phase C；需先在新对话单独授权最小 hash canonicalization 回归，随后使用新的 v3 task/run root。

**2026-09-08 v3 启动证据（Phase C 尚未完成）：** 新增回归先在旧代码下以 `ValueError: configured kernel_gt_sha256 does not match kernel_gt_path` 红灯（`red.log` 退出码 `1`），再将 `ddm4ip/trainers/deepinv_denoiser.py` 的比较改为大小写不敏感且保留 writer 的小写 canonical SHA；绿灯 `1/1`、退出码 `0`。随后 v3 launcher 退出码为 `0`，reserved spec 已写入新 run root；启动快照确认 task 为 `Running`、`LastTaskResult=267009`，状态已为 `RUNNING`，runner 与 `ddm4ip.main` 子进程均存在。当前尚未有 `plots` 结果，故不勾选 postflight、指标方向或 Phase C 完成条目；v2 的失败证据保持不变。

**2026-09-08 v3 失败证据（Phase C 未完成）：** v3 任务终态为 `Ready`、`LastTaskResult=1`，`status.json` 为 `FAILED` 且 `exit_code=1`；`status-history.jsonl` 严格为 `RESERVED -> RUNNING -> FAILED`。`task.log`（8191 字节，SHA-256=`D2B57876ECFA60928072BF728DC0A8A3C9F7B337532609E48A7F97FB2065F1AF`）记录真实 traceback：`ddm4ip/trainers/deepinv_denoiser.py:413 -> :332` 调用 `ddm4ip/losses/deepinv_loss.py:186` 的 `physics.A`，在 DeepInv `Blur.conv2d` 处因 `Input type (torch.FloatTensor)` 与 `weight type (torch.cuda.FloatTensor)` 不一致而失败。v3 `plots` 文件数为 `0`，没有 prediction/kernel/manifest/metrics/summary，因此不能把本次运行视为 Phase C 成功。该根因与已修复的 hash canonicalization 无关；按边界停止扩展修改，不重跑、不删除 v3 证据，也不启动训练或正式 500 图评估。

**2026-09-09 v6 最终成功证据（Phase C 正式关闭）：** v6 external spec SHA-256=`569DCF1A030515A2903BE00FEF48783109DA061FCB29C79F38875A867CEFAAF7`；reserved `spec.json` SHA-256=`618D6ED31BFED67C453B1D557282454ECB5FEE52BB67B5CD41C3B8106FFE07F6`；run root 为 `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot-v6`。Task Scheduler `LastTaskResult=0`，`status-history.jsonl` 严格为 `RESERVED -> RUNNING -> SUCCESS`，`status.json` exit_code=`0`，task.log SHA-256=`8F972AF6830F2AA4ED2D59C1BCD20E7B7F9C2331A3B608B64E0A7A5A7305E3EA`，没有重复触发或残留进程。

v6 独立审计重新读取 manifest/metrics/summary、16 个 prediction、16 个 kernel 及 dev-reserve pairs；summary SHA-256=`597EBD8F99E71FCA72C7E0572F71D8AF88F2076F771DC2CD1823277709208216`，manifest SHA-256=`096F7B02970723851D737B2F7B486B57311ABC834BA843D2D71665323C0B1903`，metrics SHA-256=`28A99AAFF83EF29593E03EE8370F98CAD6D4D595B72F268FAF7375C935A60F87`。kernel 全部为 `1×1×30×30`、有限、非负、sum=`0.9999990463256836`；input 均值为 PSNR=`19.537445425987244`、SSIM=`0.399074824526906`、LPIPS=`0.6320396475493908`，restored 均值为 PSNR=`26.53449785709381`、SSIM=`0.8099273145198822`、LPIPS=`0.23762223310768604`，三项方向全部通过。

Phase C / Task 10 Oracle GPU pilot 已正式关闭；Task 11 仍需用户在新的对话中单独明确授权，不得由本条记录自动启动。

## 8. Phase D：Task 11 Step 1 pilots

**必须新对话授权 pilot；该授权不含 full training。**

- [x] b01、b02、b04、b08、b16 已通过全新 Scheduled Task/run root 完成并独立验收；b32 尚未授权、尚未启动。
- [x] b02 已在 2026-09-09 通过全新 external spec、Scheduled Task 和 run root 启动，并完成独立终态验收：Task Scheduler LastTaskResult=0，history 严格为 RESERVED -> RUNNING -> SUCCESS，无重复终态，status/log/checkpoint pair 与内部 1024/1025 计数均通过。
- [x] b02 终态独立验收已通过；详细 hashes、日志、scheduler 和 checkpoint 证据见 Section 16。
- [ ] 每个 pilot 固定 `n_accum_steps=8`，分别使用 `(batch,max_steps)=(1,512),(2,1024),(4,2048),(8,4096),(16,8192),(32,16384)`，即 64 optimizer updates。
- [ ] 每个运行完成后独立验收状态、日志、有限 loss、显存、终点 checkpoint pair、文件名/SHA、内部 `N/N+1` 和 `flow_nn`，再授权下一个 batch。
- [ ] 只有 b32 低于约定显存门并通过全部验收，才允许进入 Step 1 full；若失败，必须回到新的 batch/累积设计决策，不得静默改变优化统计。

## 9. Phase E：Task 11 Step 1 full

**必须在 b32 通过后新对话单独授权。**

- [ ] 固定 `batch_size=32`、`n_accum_steps=8`、`max_steps=5242880`、`save_every_steps=2097152`、`plot_every_steps=131072`、`report_every_steps=16384`。
- [ ] 只通过 Scheduled Task 启动；一次确认后交给用户查看，不持续轮询。
- [ ] 完成后独立验收 `training-state-5242880.pt` 内部 step `5242880`、`network-snapshot-5242880.pkl` 内部 step `5242881`，两者均含 `flow_nn`，记录完整 SHA 和 resolved config。
- [ ] 只有正式终点 pair 通过，Task 12 Step 2 pilot 才准入；较早周期 checkpoint 不能替代终点。

## 10. Phase F—H：Task 12—14 后续边界

- [ ] **F1 Step 2 pilot：** 新对话，seed 0，只加载已核验 Step 1 `.pt`，clean-only 100 图、`max_val_batches=0`，不向优化暴露 `k_gt`。
- [ ] **F2 Step 2 full：** 再开新对话，seeds `0..4` 独立目录；每个终点 `.pt/.pkl` 按 `N/N+1`、`kernel_nn` 和 SHA 独立验收，并产生五个 kernel PSNR/NCC JSON。
- [ ] **G Task 13：** 新对话先跑正式 500 图 Oracle，再按 seed 0—4 跑 learned；六组 solver config hash 必须相同，唯一允许变化的是核。
- [ ] **H Task 14：** 新对话运行已在 A6 修好的聚合器，复核全部 JSONL/PNG/核结果，报告 input、Oracle、每 seed、跨 seed mean/std、失败数和研究边界。

## 11. 每阶段结束时如何更新本文

每次有实质进展，执行者必须在远端 canonical 文件中完成以下更新，并把刷新后的本文交还用户：

1. 只勾选有新鲜证据支持的条目；失败项保持未勾选，并在相应阶段下补一条带日期的失败证据。
2. 将第 2 节的 `当前总状态` 改为下一未完成阶段。
3. 在远端 `WORKLOG.md` 同步记录命令、测试数、退出码、task/run root、哈希、已知问题和下一准入。
4. 不把 `RUNNING`、Task Scheduler 的 `Ready`、单个退出码 0 或旧测试绿灯写成阶段完成。
5. 不改写旧 `FAILED`/`RESERVED` 运行根，不删除部分工件，不用新结果覆盖历史证据。

建议用户每次只说一个阶段，例如：

```text
我附上最新总计划。远端 WORKLOG 显示 Phase A 已完成，本对话只授权 Phase B；其余阶段仍不授权。
```

或：

```text
我附上最新总计划。Phase C 的计划任务已经显示结束；本对话只授权只读独立验收 Task 10，不授权重新运行、训练或正式评估。
```

## 12. 最终完成定义

只有以下条件全部成立，才能说“Task 10 已解决，可以进入 Task 11”：

- [x] Phase A 代码、runner、wrapper、schema、checkpoint 和聚合修正全部通过无训练验收。
- [x] Phase B AlexNet + DRUNet + DPIR 在规范 D 盘缓存中通过网络守卫下的实际离线构造。
- [x] Phase C 16 图 Oracle 真实 GPU pilot 的状态、日志、工件、哈希、有限指标和三项改善方向全部独立通过。
- [x] 远端 `WORKLOG.md` 已记录以上事实、关键路径和下一阶段授权边界。
- [ ] 用户在新的对话中明确授权 Task 11 Step 1 pilot。

即使前三项通过，也只准进入 Task 11 pilots；不自动授权 Step 1 full training。Task 11 full、Task 12、Task 13 和 Task 14 仍分别受独立门禁约束。



## 13. 2026-09-08 Phase C physics device 修复与 Oracle pilot v4（历史失败证据；不代表当前状态）

- [x] 按 TDD 新增 `tests\test_physics_device_mismatch.py`，旧代码 RED 退出码 `1`，证据为 `D:\DDM4IP-runtime\temp\phaseC-device-mismatch-red-20260908\red.log`；最小修复只改 `ddm4ip\losses\deepinv_loss.py` 的 `reprojection_metrics`，优先使用 `physics.device` 并回退到 buffer/输入 device。GREEN 为 1/1、退出码 `0`。
- [x] 实际 device 追踪确认 DeepInv `Blur` 的 filter/buffer 在 `cuda:0`、parameters 为空，而 restored/observation 在 CPU；根因是旧逻辑仅从 parameters 推断 device。修复后聚焦回归通过，修复文件 SHA-256=`6BA878590F411ABFD008E4B9F44F67B4159348847004BA1A859EB633893F6502`，测试 SHA-256=`590B7745A8ACD1D2F9E3E6C6059B8ECE0A66406AEDDA0BABE86F39513F1ACAB3`。
- [x] 完整 no-training unittest `69/69`、退出码 `0`；四个 synthetic Hydra `--cfg job --resolve` 均退出码 `0`；AlexNet/DRUNet/DPIR offline gate 在 `HF_HUB_OFFLINE=1`、`TRANSFORMERS_OFFLINE=1` 下通过，network guard hits=`0`。
- [x] 创建新 spec `D:\DDM4IP-runtime\experiments\phaseC-oracle-pilot-spec-20260908-v4.json`，SHA-256=`5F4CF01E232041DB0CA1BBCCD3E5C65D3D842648E0736834D7C4F1FE23BE80C0`；新 task=`DDM4IP-BDD100K-SYNTH-Oracle-Pilot-v4`；新 run root=`D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot-v4`。v1/v2/v3 未覆盖。
- [x] 仅使用 `start_bdd100k_synthetic_task.ps1` 启动 v4；launcher 退出码 `0`，启动日志 SHA-256=`7B76EEE3C9FC5BA2FD9990BD2FB5E3F23797BB0CDC28DD13AFEB60723C7D2141`。启动后只做一次快照：task `LastTaskResult=267009 (0x41301)`，run root 和 `environment.json/spec.json/status.json/status-history.jsonl/task.log` 均存在，快照时 `status=RESERVED` 且执行 PowerShell 进程存在。
- [ ] v4 终态和独立后验尚未完成；尚未验证 `status-history.jsonl` 无重复触发、`task.log`、LastTaskResult 终态、16 个唯一 source、16 个 prediction/kernel、manifest/metrics/summary SHA 链、文件尺寸/有限性/归一化以及 PSNR/SSIM/LPIPS 三项 Oracle 方向。
- [ ] Phase C 未完成；若 v4 出现与该 device mismatch 无关的新根因，保留完整失败证据并停止扩展修改。即使 v4 全部通过，也不自动进入 Task 11，需下一新对话明确授权。

关键证据：RED=`877D7BF3C319FC0BE0B59BA3BB15B19FF6BFF627AC572D1C71B6E8DDC70E8890`；GREEN=`44C1A936AE95FC1901E0AF73AF6A7784AD8DA3434D85A8830B46EA54F0A30F50`；完整 unittest=`72094551223BAE9C6F8D29E20E27FC351B5CA97F0062F3F2A9AB83DEE666AD36`。

## 13.1 2026-09-08 v4 failure evidence

- [x] 用户返回后仅做一次新的只读终态核验：DDM4IP-BDD100K-SYNTH-Oracle-Pilot-v4 为 Ready、LastTaskResult=1，status.json 为 FAILED、exit_code=1；完整 JSON 对象解析后的 status-history.jsonl 严格为 RESERVED -> RUNNING -> FAILED，未观察到重复终态。
- [x] v4 task.log 为 7387 字节，SHA-256=94E6835E2E8662C212BC9E45F56CC8E5A6D064F73475EE390C69246667747762，准确失败为 ValueError: complete source and paired-image metadata is required，位置为 ddm4ip/trainers/deepinv_denoiser.py:413 -> :384、ddm4ip/utils/benchmark_metrics.py:204。这是新的 paired-image metadata 根因，不是 CPU/CUDA physics mismatch；按边界停止扩展修改。
- [x] v4 运行根存在，plots 只有 1 个 prediction 和 1 个 kernel，没有 manifest/metrics/summary；因此完整 16 图 postflight、哈希链、有限性/归一化和三项 Oracle 指标方向均未通过，Phase C 保持未完成。v1/v2/v3 运行根和失败证据保持不变。
- [ ] 不得把该失败升级为 Phase C 完成；不得在本授权内修复 metadata、重跑 v4、创建 v5 或进入 Task 11。后续若继续，需新对话中明确授权 paired-image metadata 的最小 TDD 修复及全新 v5 Oracle pilot。
## 13.2 2026-09-09：paired-image metadata 修复与 Oracle pilot v5（历史失败证据；不代表当前状态）

### metadata 链路与 TDD

- [x] 新鲜复核 v4 的 `FAILED`、`exit_code=1`、`LastTaskResult=1` 和 `RESERVED -> RUNNING -> FAILED`；v1/v2/v3/v4 证据保持不变。
- [x] 定位唯一丢失点：`pairs.jsonl` 含且校验 `source_sha256`，但旧 `ManifestPairedDataset.__getitem__` 未把它写入 `Batch.meta`；collate、device move 与 writer 不丢字段。
- [x] 先补回归断言并确认 RED `KeyError: 'source_sha256'`，再在 dataset meta 映射中加入该字段，目标测试 GREEN；未改变设计、划分、退化、指标、输出 schema 或路径合同。
- [x] 用真实 dev-reserve 首样本验证 manifest -> dataset -> collate -> device move -> writer 所需六字段完整。

### v5 启动前门禁

- [x] 相关聚焦回归 `35/35`、退出码 `0`。
- [x] 完整 no-training unittest `69/69`、退出码 `0`。
- [x] 四个 synthetic Hydra `--cfg job --resolve` 全部退出码 `0`。
- [x] 复核 AlexNet/DRUNet 精确字节数与 SHA-256；在 `HF_HUB_OFFLINE=1`、`TRANSFORMERS_OFFLINE=1` 和网络守卫下实际构造 LPIPS AlexNet、DRUNet、DPIR，退出码 `0`、guard hits=`0`。
- [x] 临时离线记录器首版的 `StopIteration` 失败证据保留；其发生在三模型构造后，仅源于 DPIR wrapper 无直接 parameter 的记录逻辑。新 v2 证据目录修正设备解析后通过，未改项目代码。

### v5 调度与终态验收

- [x] 创建全新 external spec、任务 `DDM4IP-BDD100K-SYNTH-Oracle-Pilot-v5` 和运行根 `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot-v5`，未覆盖 v1/v2/v3/v4。
- [x] 仅通过 Windows Scheduled Task 启动；启动后只做了一次 task/process/status/history/task.log/run root 快照，没有持续轮询。唯一快照时任务已终态失败。
- [ ] 完成后独立验收 `SUCCESS`、`exit_code=0`、`LastTaskResult=0`、history 严格 `RESERVED -> RUNNING -> SUCCESS` 且无重复触发。
- [ ] 验收 16 个唯一 source、16 个 prediction、16 个 kernel、完整 manifest/metrics/summary 和全部 SHA 链；图像/核有限、尺寸正确、核非负归一化。
- [ ] 验收 restored PSNR/SSIM 均值高于 input、restored LPIPS 均值低于 input；完成后仍不得自动进入 Task 11、训练或正式 500 图评估。

### v5 终态与停止边界

- v5 launcher 退出码为 `0`，只通过 Windows Scheduled Task 启动；external spec SHA-256=`A33DB192DC762DA149D62EE8264EA76E749C436ABAB8BAD23DE5B02ABA812AC2`。
- 唯一启动快照已获得终态：Task `Ready`、`LastTaskResult=1`，`status=FAILED`、`exit_code=1`，history 严格为 `RESERVED -> RUNNING -> FAILED`，无匹配进程和重复触发。
- v5 `task.log` SHA-256=`76FD74054948265F1ACC7EB384D166150D54375EBFBAA4C8F94EF4AF5EE94A1B`。metadata `ValueError` 未复现；新错误为 DeepInv `physics.A_adjoint` 中 `0 x 0` filter 导致 `conv_transpose2d` reshape 失败。
- 此根因与 paired-image metadata 无关。依本轮授权边界保留全部证据并停止：不修改新链路、不创建 v6、不进入 Task 11、训练或正式 500 图评估。
- Phase C 保持未完成；SUCCESS、16 图完整产物、SHA 链、有限性/归一化和指标方向复选框均不得勾选。继续处理须由用户在新对话中单独授权该 filter 几何根因及新的 pilot。


## 14. 2026-09-09：Task 11 Step 1 b01 独立终态证据

- [x] 仅授权并启动 DDM4IP-BDD100K-SYNTH-Step1-Pilot-b01；主机为 DESKTOP-KBM1345，run root 为 D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-pilot-b01，external spec SHA-256=A2040469FD2DDD9114CDEF841F94BB36DC8D93F8357BBFA500D254214FFEBC59，launcher 退出码=0。
- [x] b01、b02、b04 已在 2026-09-09 通过全新 Scheduled Task/run root 完成并独立验收；b08/b16/b32 尚未授权、尚未启动。
- [x] Task Scheduler LastTaskResult=0、无 missed run、无匹配进程；status.json 为 SUCCESS/exit_code=0，完整 history 严格为 RESERVED -> RUNNING -> SUCCESS，无重复终态。
- [x] task.log 为 8030 字节、SHA-256=8964F7AE9E54A8B0A989A6296A413AE6A18F7A1DD3950424C8DC49F78C65C0C9；status.json SHA-256=E6422F31EA573E3E0AB9F14C2A2042333D62F361D39B90C494A123412260FF33；status-history.jsonl SHA-256=A9B06EA9E440676207881598B49056CD04FD6646253382723F1C3FE62ADE264F。
- [x] 终点 pair 为 training-state-512.pt（SHA-256=425E0A3506EC00D5D8492356DCD41563EE951CBECA575DAF03937A532FF5CADB，内部 global_step=512）和 network-snapshot-512.pkl（SHA-256=D951CFFDEFA595F121BD97B52245282DC5121AA60CB2C24803612AF2CADBB88E，内部 global_step=513）；两者均含 flow_nn，checkpoint 张量均有限。
- [x] 终态 GPU 快照为 RTX 2070 SUPER 469/8192 MiB、0% 利用率；这是终态显存而非峰值。完整日志没有 NaN/Inf/Infinity/nonfinite；由于 report_every_steps=16384 > 512，没有逐步数值 loss 曲线，故将“全量终点张量有限 + 日志无非有限标记”记录为当前有限性证据，并保留该审计限制。
- [x] b01、b02、b04 已在 2026-09-09 通过全新 Scheduled Task/run root 完成并独立验收；b08/b16/b32 尚未授权、尚未启动。
## 15. 2026-09-09：Task 11 Step 1 b02 启动证据（终态见 Section 16）

- [x] 本轮仅授权 b02；未启动 b04、b08、b16、b32、Step 1 full、Step 2、Step 3 或正式评估，未覆盖 b01 或其他历史 run root。
- [x] 新 external spec 为 `D:\DDM4IP-runtime\experiments\phaseD-step1-pilot-spec-20260909-b02.json`，SHA-256=`A4E416DBF25E2D71CB8AEB72F0E4BA8A21BABF5AD82BB01F903EDBEB2C79E094`；固定 `batch_size=2`、`max_steps=1024`、`n_accum_steps=8`。
- [x] 仅通过 `D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1` 启动 `DDM4IP-BDD100K-SYNTH-Step1-Pilot-b02`，launcher 退出码 `0`；run root 为 `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-pilot-b02`。
- [x] 启动后只做存在性确认：初次快照 task 为 `Running`、匹配进程数为 `3`，run root、`status.json`、`status-history.jsonl`、`task.log` 均存在；随后一次干净快照 task 为 `Ready`、匹配进程数为 `0`，上述文件仍存在。没有读取状态内容、没有判定终态、没有持续轮询。
- [x] 已独立读取 b02 终态并核对 status/history/task.log、LastTaskResult、无重复触发、有限性和终点 checkpoint pair；详细证据见 Section 16。

## 16. 2026-09-09：Task 11 Step 1 b02 独立终态验收通过

- [x] b02 仅使用已记录的 external spec D:\DDM4IP-runtime\experiments\phaseD-step1-pilot-spec-20260909-b02.json（SHA-256=A4E416DBF25E2D71CB8AEB72F0E4BA8A21BABF5AD82BB01F903EDBEB2C79E094）和全新 run root D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-pilot-b02；reserved spec.json SHA-256=01F78CC5C1BF16EFB9476554B4249AB846CBBEA87C079F7821A5865A8954FD4B。overrides 为 batch_size=2、max_steps=1024、n_accum_steps=8，global batch size=16，对应 64 次 optimizer updates。
- [x] Scheduler 为 Ready、LastTaskResult=0、无 missed run，匹配进程数为 0；status.json 为 SUCCESS/exit_code=0，SHA-256=B684750448CCFF702F473601DAC41084E19E328AF72EBA150A2C0C6B68FEC8FD；完整 history 按 JSON 对象边界解析为 RESERVED -> RUNNING -> SUCCESS，共 3 个对象、无重复终态，SHA-256=FFB982E1E2003F6047851F5D7BED14720B4380C0B83842D6EE85D7F39E18AC97。
- [x] 完整 task.log 为 8037 字节，SHA-256=3589F0F59EBBEA0B87C1854AFA426D5C5F6496F1FEF2ACCCF0FBEA761BC96734，包含终点保存和 Training finished at step 1024，无独立词边界 NaN/Inf/Infinity/nonfinite。
- [x] training-state-1024.pt 为 67265000 字节、SHA-256=7990B8B09D7511EA1DA5D045BD006A3901F66FC225BB16533BF9656D8C412DC7，内部 global_step=1024，含 flow_nn，519 个张量全有限；network-snapshot-1024.pkl 为 16862877 字节、SHA-256=F4BD0DF7E62BE9B1BBAA67E7706D3E1D2E6E1AC08AAA654B9AE84E347953A811，内部 global_step=1025，含 flow_nn=RFNoPrecond，105 个模型张量全有限。pickle 临时导入路径在加载后恢复。
- [x] 结论：b02 已完成并通过本阶段的独立执行/工件门；本轮未启动 b04、b08、b16、b32、Step 1 full、Step 2、Step 3 或正式评估。下一准入仅为新对话、用户明确授权的 b04 pilot；b32 通过后 Step 1 full 仍需再次单独授权。

## 17. 2026-09-09：b02 之后的日志与规则同步

- [x] b02 的独立终态证据已在 Section 16 记录；本次同步没有创建、启动、重启或修改任何 Scheduled Task、run root、checkpoint、代码或数据。
- [x] 本机 AGENTS.md 新增 Task 11 Step 1 pilot 的通用终态验收规则，更新后 SHA-256=B0B24BD1E1586E44D658D3AC1293A4A80EA8617E89539E324349380BEAAB75BC；规则要求独立核对 scheduler、进程、status、对象边界 history、完整日志、checkpoint SHA、内部 N/N+1、flow_nn 和全量张量有限性。
- [x] b04 已按用户明确授权启动，固定 batch_size=4、max_steps=2048、n_accum_steps=8；当前下一准入为新对话中的 b04 独立终态验收。b08、b16、b32 必须按顺序逐个授权和独立验收，b32 通过前不得进入 Step 1 full。
- [x] 本次只做文档闭环；后续 pilot、full training、Step 2、Step 3 和正式评估均未获得授权。

## 18. 2026-09-09：Task 11 Step 1 b04 启动证据（终态待独立验收）

- [x] 本对话只授权 b04；未启动 b08、b16、b32、Step 1 full、Step 2、Step 3 或正式评估。
- [x] 新 external spec 为 D:\DDM4IP-runtime\experiments\phaseD-step1-pilot-spec-20260909-b04.json，SHA-256=30B865B3118A0F3A20EF10D4EC4C220E63665BA0887B69DA02219DA358AF4E1C；固定 batch_size=4、max_steps=2048、n_accum_steps=8。
- [x] 仅通过 D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1 启动 DDM4IP-BDD100K-SYNTH-Step1-Pilot-b04，launcher 退出码为 0；run root 为 D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-pilot-b04。
- [x] 启动后只做了一次存在性确认：任务对象存在，LastTaskResult=267009 (0x41301)，匹配 b04 进程数为 3，status.json、status-history.jsonl 和 task.log 均存在；未读取状态内容，未判断终态，未持续轮询。
- [ ] b04 已完成 scheduler、进程、status、对象边界 history、完整日志和终点 checkpoint pair 的独立验收；详细证据见 Section 19。b08/b16/b32 仍未授权、尚未启动。

## 19. 2026-09-09：Task 11 Step 1 b04 独立终态验收通过

- [x] 新 SSH 只读核验确认 task DDM4IP-BDD100K-SYNTH-Step1-Pilot-b04 为 Ready、LastTaskResult=0、无 missed run、无匹配进程；没有发现 b08、b16、b32、Step 1 full、Step 2 或 Step 3 的任务/进程。
- [x] external spec SHA-256=30B865B3118A0F3A20EF10D4EC4C220E63665BA0887B69DA02219DA358AF4E1C；reserved spec.json SHA-256=05122FFDC0753372F3FAE616729BF927FB94DBEDAA77EEE7710974A7BBCCE6D6。两者 run root 一致，实际 overrides 为 training.batch_size=4、training.max_steps=2048、loss.n_accum_steps=8，stage=step1、mode=pilot、variant=null。
- [x] status.json 为 SUCCESS/0，SHA-256=AB80B9ED1A53833CC81B9805668266B18F364501B3C9FD0F11C71D699ACA39F6；完整 status-history.jsonl 按 JSON 对象边界解析为 RESERVED -> RUNNING -> SUCCESS，3 个对象、1 个终态、无重复终态，SHA-256=A3144858B0B547CADFFA6EC0A62A46F1D2D9F693A1B6F9FFB3E7BFC20B0EE72C。
- [x] 完整 task.log 为 8037 字节，SHA-256=302652D7D4B0CA8A5B107CB3D703D8B5B676CF495A34287C9BBEF75DDD0EEFC6；包含终点 step 2048、checkpoint/snapshot 保存及 SUCCESS 结束标记，无独立词边界 NaN/Inf/Infinity/nonfinite。
- [x] training-state-2048.pt 为 67265000 字节、SHA-256=9137369313B2FFB2FD78C7C408F8D860CCD345DD30BC9218864E0525251C4B36，内部 global_step=2048、含 flow_nn、519 个张量全有限；network-snapshot-2048.pkl 为 16862877 字节、SHA-256=4C4B47A0E84877562A3ABED4023034D68844E887A213FC29CF92D8604EC58B9B，内部 global_step=2049、含 flow_nn=RFNoPrecond、105 个模型张量全有限。pickle 临时导入路径已恢复。
- [x] 结论：b04 通过独立执行/工件门；下一准入仅为新对话、用户明确授权的 b08。b16、b32 必须按顺序逐个授权和验收，b32 通过前不得进入 Step 1 full。

## 20. 2026-09-09：Task 11 Step 1 b08 启动证据（终态待独立验收）

- [x] 本对话只授权 b08；未启动 b16、b32、Step 1 full、Step 2、Step 3 或正式评估。启动前确认 b08 external spec、task、run root 和 reserved spec.json 均不存在。
- [x] external spec 为 D:\DDM4IP-runtime\experiments\phaseD-step1-pilot-spec-20260909-b08.json，SHA-256=E72568DB0BFAF23A59AEE7A586C0CF1745A45B0989A8640C080EE976A5A473FC；固定 batch_size=8、max_steps=4096、n_accum_steps=8；run root 为 D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-pilot-b08。
- [x] 仅通过 D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1 启动 DDM4IP-BDD100K-SYNTH-Step1-Pilot-b08，launcher 退出码为 0；Scheduled Task action 已独立核对为 -Action execute -SpecPath <run_root>\spec.json，没有把 external spec 直接传给 execute。
- [x] 启动后只做一次存在性确认：task 为 Running、LastTaskResult=267009 (0x41301)，匹配进程数为 3，run root、status.json、status-history.jsonl 和 task.log 均存在；未读取状态/日志内容，未判断终态，未持续轮询。
- [ ] b08 的终态和独立后验尚未完成；必须在用户新对话中重新授权后独立核对 scheduler、进程、status/history、完整 task.log、终点 checkpoint pair、SHA-256、内部 N/N+1、flow_nn 和全量张量有限性；在此之前不得启动 b16、b32 或 Step 1 full。


## 21. 2026-09-10：Task 11 Step 1 b08 独立终态验收通过

- [x] 本轮只做 b08 的新鲜只读终态验收；未重启或重跑 b08，未启动 b16、b32、Step 1 full、Step 2、Step 3 或正式评估。
- [x] DDM4IP-BDD100K-SYNTH-Step1-Pilot-b08 为 Ready，LastTaskResult=0，NumberOfMissedRuns=0，匹配 b08 的进程数为 0。Scheduled Task action 使用 run_bdd100k_synthetic_stage.ps1 -Action execute -SpecPath D:\DDM4IP-runtime\experimentsdd100k-synthetic-motionblur-v1-step1-pilot-b08\spec.json，未把 external spec 直接传给 execute；未发现 b16、b32、Step 1 full、Step 2 或 Step 3 的任务/进程。
- [x] external spec D:\DDM4IP-runtime\experiments\phaseD-step1-pilot-spec-20260909-b08.json SHA-256=E72568DB0BFAF23A59AEE7A586C0CF1745A45B0989A8640C080EE976A5A473FC；reserved spec.json SHA-256=0F7BED952E8671A0AD6D5F9444CFA1059EEEE1261F340CB67A3CE4D9AE0B774A。两者均绑定 run root D:\DDM4IP-runtime\experimentsdd100k-synthetic-motionblur-v1-step1-pilot-b08，overrides 为 training.batch_size=8、training.max_steps=4096、loss.n_accum_steps=8；global batch size=64，对应 64 次 optimizer updates。
- [x] status.json 为 SUCCESS/0，SHA-256=CAAE847FF1F2710518109611A9290088BAF874891C2C4EE8788C2944C41ABED5；完整 status-history.jsonl 按 JSON 对象边界解析为严格 RESERVED -> RUNNING -> SUCCESS，共 3 个对象、1 个终态、无重复终态，SHA-256=C39BF6D7A3C92D1FE261F42BA04ACBFE28918A8EE1510190B3BCE81316AEB6EB。
- [x] 完整 task.log 为 8037 字节，SHA-256=61B61AAA68BC9FD146764BAB17E926455204483DD72674006B09D3698B8BFE14；包含 Training finished at step 4096、终点 checkpoint/network snapshot 保存和 execution finished: status=SUCCESS exit_code=0，独立词边界检查未发现 NaN/Inf/Infinity/nonfinite。
- [x] 终点 pair 均存在：training-state-4096.pt 为 67265000 字节、SHA-256=D48BACDDF15E2DFA9496850A0BB81D7766841A209C36A3D048ED82DA419CA9D4；network-snapshot-4096.pkl 为 16862877 字节、SHA-256=53339BCEE6716034CDA6D405C8F98BA33678D0F248D590173A7D5C18ACE6CCC7。
- [x] 使用远端 E:\Anaconda3\envs\ddm4ip\python.exe 独立加载 checkpoint：.pt 内部 global_step=4096，含 flow_nn，递归发现 519 个张量且全部有限；.pkl 内部 global_step=4097，含 flow_nn=RFNoPrecond，模型 state dict 的 105 个张量全部有限。pickle 加载前确认仓库根不在 sys.path，临时加入后已恢复原路径；独立审计脚本 v2 SHA-256=e6359b1a3af70f3734194c13fc6953a0ba1b9928c5368113eb59d8d886260864，退出码为 0、AUDIT_RESULT PASS。
- [x] 结论：b08 已通过 Task 11 Step 1 pilot 的独立 scheduler/执行/工件门。下一准入仅为新对话中用户明确授权的 b16；b16 通过后才可申请 b32，b32 通过且满足显存/有限性门后仍需另一个新对话单独授权 Step 1 full。
## 22. 2026-09-10：Task 11 Step 1 b16 启动证据（终态待独立验收）

- [x] 本对话只授权 b16 pilot；未授权 b32、Step 1 full、Step 2、Step 3 或正式评估，也未重启或重跑 b08。
- [x] 启动前新鲜核对 b08 为 Ready、LastTaskResult=0、status=SUCCESS/0，终点 checkpoint pair 和三份状态/日志文件均存在；b16 external spec、task、run root 均不存在，b32/Step 1 full/Step 2/Step 3 相关任务不存在，匹配项目进程数为 0。
- [x] b16 external spec 为 D:\DDM4IP-runtime\experiments\phaseD-step1-pilot-spec-20260909-b16.json，SHA-256=F873C8529ECC4B561A62900EB73B1A533BC3FF9EDC6C846ED8525C630E88E847；固定 stage=step1、mode=pilot、variant=null、expected_manifest_records=1000，overrides 为 training.batch_size=16、training.max_steps=8192、loss.n_accum_steps=8。
- [x] b16 run root 为 D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-pilot-b16，Scheduled Task 为 DDM4IP-BDD100K-SYNTH-Step1-Pilot-b16；global batch size=128，对应 64 次 optimizer updates。
- [x] 仅通过 D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1 注册并启动，launcher SSH/远端退出码为 0；未 direct 执行 runner、stage wrapper 或训练模块。launcher 的 execute 合同使用 prepare 生成的 run_root\spec.json。
- [x] 唯一启动后存在性快照：任务对象存在、状态为 Running、LastTaskResult=267009（0x41301）、匹配 b16 项目进程数为 3；run root、status.json、status-history.jsonl 和 task.log 均存在。
- [ ] 尚未读取 b16 状态/日志内容或判断 SUCCESS/FAILED，尚未完成终态 checkpoint/SHA、内部 N/N+1、flow_nn、全量张量有限性和显存独立验收；在用户新对话重新授权前不得启动 b32、Step 1 full、Step 2、Step 3 或正式评估。
## 23. 2026-09-10：Task 11 Step 1 b16 独立终态验收通过

- [x] 新 SSH 只读核验确认远端主机为 DESKTOP-KBM1345；DDM4IP-BDD100K-SYNTH-Step1-Pilot-b16 为 Ready，LastTaskResult=0，NumberOfMissedRuns=0，LastRunTime=2026-09-10T09:42:45+08:00，匹配 b16 运行根/spec 的项目进程数为 0。b32、Step 1 full、Step 2、Step 3 相关任务与匹配进程均为 0。
- [x] b16 external spec 为 D:\DDM4IP-runtime\experiments\phaseD-step1-pilot-spec-20260909-b16.json，SHA-256=F873C8529ECC4B561A62900EB73B1A533BC3FF9EDC6C846ED8525C630E88E847；reserved spec.json 为 1287 字节，SHA-256=821599165EBE87DDBDCDF928BB50833891B6B12B60E5C385990CB4923BDC17AC；run root 为 D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-pilot-b16，overrides 为 batch_size=16、max_steps=8192、n_accum_steps=8，global batch size=128，对应 64 次 optimizer updates。
- [x] status.json 为 SUCCESS/0，457 字节，SHA-256=E414686780685516E035C3064163E5AFE416936E0D2CBB89C45392B62CD6EF29；完整 status-history.jsonl 为 953 字节，SHA-256=2335B921C4E9945626A0FF54EF474A153A574EC0CC302975961697CD0E6C5EB6，按 JSON 对象边界严格为 RESERVED -> RUNNING -> SUCCESS，共 3 个对象、无重复终态。
- [x] 完整 task.log 为 8071 字节，SHA-256=54B0A40305094F254EDB085DFC3648B179F68FBE696769C9E22368946809B1A6，包含 Training finished at step 8192、终点 checkpoint/network snapshot 保存和 SUCCESS 结束标记；没有独立词边界 NaN/Inf/Infinity/nonfinite。
- [x] training-state-8192.pt 为 67265000 字节、SHA-256=C65555B401385D7CFD92080A0716A5434C45C05B1A1F165DB81CC0138664F5C2，内部 global_step=8192、含 flow_nn、519 个张量全有限；network-snapshot-8192.pkl 为 16862877 字节、SHA-256=15E1D646A4E8E170C2888F33B9B9CAE143534B72BE77C68445E052A3AA6D701E，内部 global_step=8193、含 flow_nn=RFNoPrecond、105 个模型张量全有限。pickle 临时 sys.path 已恢复；独立审计脚本 SHA-256=1B5D6898CC9BDD19873642429263099A817E5672198A99CD96104643EE9B1E77，退出码 0，AUDIT_RESULT PASS。
- [x] 结论：b16 通过 Task 11 Step 1 pilot 独立终态门。下一准入仅为新对话中用户明确授权的 b32；b32 通过并完成独立验收后，Step 1 full 仍需再次单独授权。历史 b16 启动条目 Section 22 保留为当时终态待验收记录，不改写历史证据。

## 24. 2026-09-17: Source publication closure and next-stage boundary

- [x] Owner explicitly selected complete source/documentation publication, excluding datasets, weights, and checkpoints. The destination is the public repository https://github.com/saadxxx847-ai/Unsupervised-Imaging-Inverse-Problems.
- [x] Full startup verification and complete reading of the approved design/original implementation plan were completed. Remote WORKLOG, including its appended b16 formal launch record, remains the project fact source. Historic task checkboxes above are retained.
- [x] Published source commit 4ab521428fa0cc6de4a5a660f7a79df68b50045e from an isolated personal-computer Git copy. Preserved all five upstream commits and MIT license, 197 original source files, plus eight runtime source copies and publication documentation/manifests (209 files total). Both archive transfers matched SHA-256; git fsck and push exited 0; an independent GitHub API read matched every published blob SHA.
- [x] Source copies of previously external orchestration files are now preserved under scripts/orchestration in the GitHub publication. Their active D:\DDM4IP-runtime\orchestration deployments were not changed; publication did not register or start a task. This is a source-publication scope extension, not a change to the experiment protocol.
- [x] Remote Git stayed read-only and its index remained unchanged. Local upload location and exact archive hashes/cleanup paths are recorded in WORKLOG's 2026-09-17 appendix. No project tests, data processing, training, inference, or evaluation were run.
- [ ] Independent terminal acceptance of the existing b16 formal run remains pending. The publication-time scheduler snapshot was Ready / LastTaskResult=0; this alone does not certify the formal checkpoint. Do not equate the user's reported network interruption with proven training failure.
- [ ] Next conversation requires explicit authorization for read-only b16 formal acceptance: task/processes, status/history/log, frozen Scheme A configuration, final checkpoint pair SHA-256, internal steps 5242880/5242881, flow_nn keys, and all tensor finiteness. Keep the existing run root and all historical evidence unchanged.
- [ ] Step 2, Step 3, formal evaluation, data processing, weight downloads, new tasks, and restarted/resumed training remain separately authorized. This publication does not grant those permissions.


## 2026-09-18—19：Step 1 full 原生 CUDA 崩溃诊断、修复与独立重启

- 本轮授权仅为诊断并修复失败的 Step 1 full 后重启。完整启动核验、已批准的 2026-09-06 设计和实施计划、b16 fallback amendment/plan 已阅读；远端日志比本机控制日志新，以远端为准。本机 WORKLOG 未更新，远端 Git 仅只读检查，已有暂存和未提交修改保留。9 月 18 日因用量上限暂停时尚未启动新任务；9 月 19 日恢复后重新核对主机 DESKTOP-KBM1345、任务/进程及文件哈希，确认没有并发训练，修复文件和冻结 spec 未发生变化。
- 已证实的失败：旧运行根 `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-full-b16-cp-20260917` 于 2026-09-17 21:04 失败，子进程退出码 `3221225477 = 0xC0000005`。Windows Application Event 1000 将 PID 22320 的异常定位到固定环境 `torch\lib\c10_cuda.dll`，偏移 `0x1f13d`；scheduler 最后结果 `4294967295`。status/history 为 RESERVED -> RUNNING -> FAILED，没有重复终态。机器最近启动时间为 9 月 16 日，当时未重启，不能归因为 SSH 断开或断电。
- TensorBoard 最后记录的 global_step 为 `131072`（1,024 次完整更新）、loss 约 `0.10066947`，张量日志未显示非有限 loss；约 15 分钟后崩溃。位置接近首次预览生成，但没有 dump/调用栈能证明预览是触发原因。故障指令位于原生 CUDA 分配统计相关区域；不能进一步宣称已证明驱动缺陷、OOM 或特定 PyTorch bug。旧保存间隔 1048576 尚未到达，因此没有可恢复的正式检查点，本次必须从 0 开始。
- 修复：仅对 Step 1 full 进程设置 `PYTORCH_CUDA_ALLOC_CONF=backend:cudaMallocAsync`，作为绕开 native allocator 崩溃路径的工作方案；启用 `PYTHONUNBUFFERED=1`、`PYTHONFAULTHANDLER=1`，并记录 `process-policy.json`。未升级/安装 PyTorch、CUDA、驱动或其他依赖，未修改系统或用户全局环境。cudaMallocAsync 下部分 PyTorch allocator 显存统计不具可比性，不能把统计值 0 当作无显存使用。
- BaseTrainer 只解除保存间隔必须为绘图间隔倍数的限制，仍要求与 global batch 对齐，保留原有周期保存与强制终点保存。新 `save_every_steps=16384`，report 16384、plot 131072 不变。完整预算仍为 Scheme A：batch 16、accum 8、global batch 128、seed 42、max_steps 5242880、40960 次完整更新；数据、模型、损失、无配对监督和验证边界未变。预计 320 对检查点约 26.92 GB，启动前 D 盘可用约 115.13 GB。
- 测试先行证据：新增频繁保存/恢复测试在旧实现下因 save/plot 约束失败，修复后通过；恢复脚本新增试运行不移动 claim、FAILED 不重执行、SUCCESS 不重执行测试，旧实现前两项失败，修复后通过。相关 35 项 unittest 在远端固定 Python 下通过（10.798 秒，退出码 0），三个 PowerShell 脚本解析通过。额外 GPU 无优化器更新检查实际使用 Torch 2.4.1+cu118、cudaMallocAsync、b16 前后向和 16 张/32 步生成预览，非零 loss、梯度和输出有限，退出码 0。只读探针加载的是已验收 b16 pilot 权重，SHA-256 `C65555B401385D7CFD92080A0716A5434C45C05B1A1F165DB81CC0138664F5C2`；该权重未注入新 full，不能把探针当作训练产物。上述检查不能替代长时间稳定性或 full 终态验收。
- 运行器修复与恢复：新 launcher 在注册时设置 `ExecutionTimeLimit=PT0S`，单次手动启动、IgnoreNew，不受默认 72 小时截止影响。恢复脚本支持中断后仍为 RUNNING 的运行继续；FAILED/SUCCESS 均跳过，DryRun 不移动 claim/锁，检查 runner 和训练进程防止重复。旧 `DDM4IP-BDD100K-SYNTH-Step1-Full-b16-cp-recovery-20260917` 已导出 XML 后禁用，防止未来登录重启旧失败目录。新登录恢复任务 `DDM4IP-BDD100K-SYNTH-Step1-Full-b16-async-recovery-20260918` 已注册，尚未实际触发；本轮未模拟断电，不能宣称断电恢复已端到端验证。恢复依赖该远端用户登录，最新检查点若损坏应另行诊断，不能改写 FAILED 历史来重试。
- 新 external spec：`D:\DDM4IP-runtime\experiments\phaseE-step1-full-spec-20260918-b16-async.json`，SHA-256 `8F9E4513380D81D58ABAAB2657CC48E40E8FD55FCF3F811EA9CD104044277CDA`。prepare 生成的 reserved spec SHA-256 `1B963CF890AF8081FAF5F5D94DB4D94549A9D809952C0D4F6909A87C5C1A2F81`。benchmark summary/pairs/kernel 再次与冻结哈希匹配，resolved config 已独立解析；没有重建数据或扫描/改写 benchmark 像素。
- 新运行根：`D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-full-b16-async-20260918`；任务 `DDM4IP-BDD100K-SYNTH-Step1-Full-b16-async-20260918`。目录名保留 9 月 18 日冻结日期，实际于 **2026-09-19 08:01:08 +08:00** 通过 `start_bdd100k_synthetic_task.ps1` 启动，launcher/恢复任务注册退出码 0。真实 execute 使用 `<run_root>\spec.json`，没有 direct 运行训练模块。
- 唯一启动后核查于 **2026-09-19 08:01:54 +08:00** 完成：scheduler Running、LastTaskResult 267009 (0x41301)、status RUNNING、PT0S；固定 Python 的 runner PID 22068 和训练 PID 11480 存在；spec/status/history/task.log/process-policy 存在，task.log 7921 字节且最后写入晚于启动时间。实际命令包含 batch16/accum8/max5242880/save16384，policy 记录 async/unbuffered/faulthandler。只确认启动，不等待训练完成、不持续轮询。
- 核心修复哈希：`ddm4ip\trainers\base.py` = `9C4F7671C631ED6532950A667E92AAB74D57C762ED1E0A06E538B8160F4D0439`；stage wrapper = `CB6195A01A03FB1603B1631A79F3132C8CE1876A1B105D2B9426757C65E3D1B1`；launcher = `CA3A76708573EECDF6A6BCC6DF27FAA6B86BC5475299B6705A68B6100D4D3C77`；recovery wrapper = `45328E451B1FE8FB8387E29A12A2CFCB965E056B789F3F27CCD6B461DE92453C`。完整测试/修复哈希、原始备份、故障事件/WER、TensorBoard 摘要、RED/GREEN/35-test 日志、GPU 探针、resolved config、preflight、launch-verification.json 和启动日志快照见 `D:\DDM4IP-runtime\diagnostics\step1-crash-20260918`。旧失败 spec/status/history/task.log 保持原 SHA-256，所有旧运行目录原样保留。
- 清理清单（均为本项目专用，当前保留）：上述 diagnostics 目录、新 external spec、新运行根、两个新任务（training/recovery）、修改的 `D:\DDM4IP-runtime\orchestration` 三个脚本，以及本机控制暂存目录 `D:\Unsupervised Imaging Inverse Problems\restart-diagnosis-20260918`。测试保留的精确临时目录见 diagnostics 下 `cleanup-inventory.json`，包含本轮 pycache 和测试日志；未新增依赖环境、权重或数据集，不删除公共缓存。旧失败运行根和旧任务 XML 属于证据，不清理；不执行批量删除。
- 已完成范围为失败定位、工作方案实施、相关测试和本次 full 启动确认；**尚未完成**长期稳定性和 full 终态验收。用户可在组里电脑 PowerShell 运行下面命令，Ctrl+C 只停止日志跟随，不会停止训练。远端电脑需保持开机；本机与 SSH 可关闭，没有未完成传输。

```powershell
$run = 'D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-full-b16-async-20260918'
Get-Content -LiteralPath "$run\status.json" -Raw
Get-ScheduledTask -TaskName 'DDM4IP-BDD100K-SYNTH-Step1-Full-b16-async-20260918' | Get-ScheduledTaskInfo
Get-Content -LiteralPath "$run\task.log" -Tail 50 -Wait
```

- 下一准入：用户观察到 SUCCESS 或 FAILED 后，在新对话明确授权只读独立验收。必须交叉核对任务/进程、status、按完整 JSON 对象边界解析的 history、完整日志、冻结配置，以及最终 `training-state-5242880.pt`/`network-snapshot-5242880.pkl` 的 SHA-256、内部 5242880/5242881、flow_nn 模型键与全量张量有限性。失败时保留证据，先诊断；Step 2、Step 3、正式评估和新的数据处理仍未授权。可复制提示词：“请按 AGENTS.md 完成完整启动核验，读取远端最新 WORKLOG 和批准文档；本次只独立验收 step1-full-b16-async-20260918 的终态、日志、预算和终点检查点。如失败先诊断并报告，不自动重启，不启动 Step 2/3。”

## 2026-09-19：全项目系统性代码审查与隔离修复完成，尚未部署

- 授权范围：全项目代码审查、必要的隔离修复和无训练 CPU 验证；不停止/重启现有训练，不占用 GPU，不改变预算，不启动 Step2/3、正式评估、数据重处理或新的计划任务。完整启动核验及批准设计/计划、b16 fallback amendment/plan、canonical plan 已读。本机 WORKLOG 较旧，仅作为辅助上下文，未更新。
- 唯一训练状态观察：`DDM4IP-BDD100K-SYNTH-Step1-Full-b16-async-20260918` 在本轮开始时为 Running，LastTaskResult=267009，wrapper/runner/train PID=23936/22068/11480；日志观察到 step16384/32768 保存。实际 batch16、accum8、max5242880、report/save16384、plot131072，async/unbuffered/faulthandler。此观察不代表终态；没有再次轮询或干预训练。
- 审查独占根：`D:\DDM4IP-runtime\code-audit\20260919-systematic`。baseline/candidate 分别包含194个仓库文本/源码/配置文件和9个实际 `D:\DDM4IP-runtime\orchestration` 文件，未复制 .git、数据、权重或训练检查点。所有实现修复只在 candidate；当前运行的原仓库和部署脚本没有应用补丁。
- 完成27类有失败证据支持的问题修复：P1=20、P2=7。主要包括终点恢复超预算、非整批预算、异常后仍更新参数、AMP跳步推进scheduler、检查点半写、Step2 seed未注入、无效配对验证override、Downsampling与DirectKernel固定版本构造崩溃、核几何/PSF轴序、非有限预测被clamp掩盖、claim竞态、缺失训练postflight、吞数据加载异常、丢分块核、忽略PNG失败、汇总身份/核种子追溯、图像缓存无限增长、EMA恢复截断以及遗留CLI。每项准确行号、触发条件、影响、证据和最小修复见 `audit-report.md`、`issues.csv/json`。
- 最终新鲜验收：`E:\Anaconda3\envs\ddm4ip\python.exe <audit-root>\run_cpu_audit.py ALL`，114项中109 PASS、5 GPU专属 SKIP、0 FAIL，25.352秒，退出码0；`IMPORT_ISOLATION_OK=79`。证据 `evidence\suite-acceptance.log` SHA-256=`6FDB8B500D88170AA859E5816C7E08A82AF0669AEE20C45ACF51D69E5F5C15FC`。所有失败/中间证据均保留；CPU标量optimizer夹具和无优化训练循环不属于学习产物训练。
- 四个独立 `python -m ddm4ip.main ... --cfg job --resolve` 配置进程退出0，五个部署PowerShell文件解析错误0；90个既有和6个新增Python文件AST解析通过。配置解析、导入或CPU夹具均不替代实际GPU入口验收。遗留Restormer导入测试使用natsort/joblib替身，当前环境缺joblib；未安装依赖或运行该预处理。
- 保护核验：文档闭环前全部203个原始文件SHA-256与审查启动清单一致；Git索引哈希保持 `2EE2DB58AFFB1845A516B7E2B86F09DBFF1FC4C27A81ED84AE7BFB8F888CC276`。证据 `preservation-before-docs.json`。本次唯一原仓库写入为本WORKLOG与canonical plan；本机AGENTS追加长期规则。未提交、推送或执行其它Git写操作。
- 交付：`audit-report.md` SHA-256=`37E4C2EE3F9A7D124B38CA70917CB0B63FB03AFE5EDE748D27148787BFA47C77`；`deployment-manifest.json` SHA-256=`3317AA99623185C3E51B3DDABD959683168400A81BBA88B3354677C97775B729`；`candidate.patch` SHA-256=`7A05391DA307F1E4F3AD19A95D2CAFE300D3B4060577AE86632DB1A14A1AA97D`。26个待部署文件为19个产品/运行器文件和7个测试文件，完整原/新哈希及精确候选和目标路径见部署清单。包含仓库外 `orchestration\bdd100k_runner.py`，不得遗漏或单独部署依赖该辅助模块的脚本。
- 未解决/未覆盖：严格断点可复现性仍缺RNG、worker和PatchDataset游标恢复；Step2数据读取计数不能由global_step简单推断。CUDA/多卡/真实DPIR与LPIPS前向、断电恢复和原生崩溃根因未验证。checkpoint临时发布不是跨两文件事务；synthetic状态写入/注册失败故障窗口仍需专门夹具。核分析snapshot与各learned评估的冻结predecessor仍需跨工件绑定核验。未重新验收正式benchmark像素/角色，未证明组内不配对图可用全参考指标。
- 清理清单：远端独占审查根及其baseline/candidate/temp/cache/evidence、报告、diff、配置与清单全部保留；当次统计2825文件、9544296字节，后续文档工件会增加。精确目录见 `cleanup-inventory.json`。本机辅助文本脚本和交付副本独占目录 `D:\DDM4IP-local-runtime\code-audit-20260919`；不安装本机或远端新环境/包，不复制数据/权重，不清理公用缓存，不执行递归或批量删除。
- 下一阶段准入：用户观察当前full终态后，必须在新对话单独授权只读独立验收。检查scheduler/匹配进程、status、按完整JSON对象边界解析的history、完整task.log、冻结配置及最终 `.pt/.pkl` SHA、内部5242880/5242881、flow键和全量张量有限性。审查修复不得自动部署；须先确认训练已结束且不再依赖旧runner恢复，再单独授权部署并逐项CAS比较live当前SHA与清单baselineSHA。不一致时停止覆盖、保留并发修改。新runner会改变旧reserved spec的runner_sha256契约，必须按新授权冻结新spec，禁止修改旧证据配合新代码。Step2/3、正式评估和数据处理仍需各自新对话明确确认。

可复制的新对话提示：

> 请按 AGENTS.md 完成完整启动核验，完整读取最新 WORKLOG、批准设计/计划、b16 fallback 文档、canonical plan，以及 D:\DDM4IP-runtime\code-audit\20260919-systematic\audit-report.md。本次只授权对 step1-full-b16-async-20260918 做新的独立终态验收，并核对审查包部署前条件；不停止或重启训练，不部署补丁，不启动Step2/3。请逐项核验任务/进程、完整状态历史、task.log、冻结配置及终点checkpoint的SHA、内部5242880/5242881、flow键和全量有限性。未结束或验收失败时保留证据并报告。


### 2026-09-19：按用户要求结束本轮并交接后续工作

用户要求将后续工作整理成文档，在新对话继续。本轮不再扩展代码修复，也不重复检查训练状态。完整交接位于 `D:\DDM4IP-runtime\code-audit\20260919-systematic\NEXT_SESSION.md`，本机交付副本位于 `D:\DDM4IP-local-runtime\code-audit-20260919\NEXT_SESSION.md`。两份文件已独立核验 SHA-256 一致：`C4AAE18A39BC000C46328F7B5CB5DF8C108D8DF81990930652A62689C4792709`。

交接包含：已完成的隔离修复及证据、剩余问题优先级、测试路径可迁移性、恢复语义限制、独立 full 终态验收条件、部署与 GPU 验证阶段门，以及两段可直接复制的新对话提示词。修复仍未部署；下一轮不得把本轮历史训练状态当成当前状态，不得自动启动后续训练、评估、数据处理或部署。

## 2026-09-19—20：交接第 4 节剩余隔离审查闭环（candidate-only）

- [x] 完整启动核验及指定材料阅读完成；远端 WORKLOG 为事实源，本机日志较旧且未更新。唯一训练新鲜快照为 18:19 +08:00 的 Running / `LastTaskResult=267009` / `status=RUNNING`，最近 checkpoint step 1327104；其后未轮询、停止或重启训练。
- [x] candidate 修改前冻结为 209 文件、聚合 SHA-256 `42F265FB5AC25DB9571310A40F12E75591D4FCBA5894FC1821B609D86229B646`；修改后为 210 文件、聚合 SHA-256 `9F0A12A69CE6723EC6C3D0849F899FC48E2B91205A4BB3E4E70158DAD47606C5`，本轮新增/修改 15 文件。baseline、旧 candidate、旧补丁/报告/证据均保留。
- [x] synthetic 状态写入已在 candidate 改为 history 追加+fsync、`status.json` 临时文件+fsync+原子 replace，终态单调；替换失败夹具证明旧 JSON 完整、history 与临时证据可审计。launcher 的 Register/Start 异常均进入 `dispatch-failed` 并写 reserved run 的 log/history/status；PowerShell mock 夹具不触碰真实计划任务。
- [x] 新 checkpoint 采用 pending/commit marker 协议；无 commit 的 pending 使恢复 fail closed，损坏最高 commit 不得回退旧 checkpoint；历史双文件 pair 保持兼容。验证 iterator 回传已修复。
- [x] learned evaluation 的逐图记录/summary 与核分析结果通过同一冻结 Step 2 snapshot SHA-256 绑定，并继续核对 seed 与真核 SHA；错误 checkpoint/seed/source 夹具均拒绝。外部 orchestration 测试只接受 `DDM4IP_TEST_ORCHESTRATION` 显式路径注入。
- [x] 最终隔离 CPU 验收：123 项运行、5 项 CUDA 条件跳过、0 fail、退出码 0，`IMPORT_ISOLATION_OK 80`；`final-all.log` SHA-256 `F7604988876E9E678A832D73BB39F86A3409DDB5279FE1F13810049FEB14EDCC`。没有 GPU、网络、依赖安装、计划任务或 live 执行。
- [x] 本轮交付根为 `D:\DDM4IP-runtime\code-audit\20260919-systematic\evidence\session4-20260919`。逐文件清单 SHA-256 `A4AE63B1930E17781C7E1BCC19A353D8D1E3454B4FCDF726C60EF8B13CD4A4A5`；累计补丁 `8551165EC52E5C8ECEB5C1DBAEA26EEDEA3F24C138985C46740EB90060B9EC9D`；测试汇总 `063BB3590C829408F26C0E4F106B9AD11C84320844249466FFC569C25FAACFB2`；补充报告 `677A3BA707F934AF1262BA5B7EFAD9FE963526F3FB176A24ECB724F5035D5CBA`。旧 `candidate.patch` 未覆盖。
- [x] live 保护复核：除开始前已知的 WORKLOG/canonical 文档更新外，原保护清单其余 201 个 live 源码、配置和部署运行器 SHA-256 不变；Git index 仍为 `2EE2DB58AFFB1845A516B7E2B86F09DBFF1FC4C27A81ED84AE7BFB8F888CC276`。本轮只更新两份项目文档，未执行 `git add/commit/push/pull/checkout/reset`，未改变 index/ref/worktree。结束核验时误调用一次 `git write-tree`，可能物化不可达 tree object；发现后未再执行 Git 写命令，也未尝试清理对象。本项为对“不得做 Git 写操作”边界的如实偏差记录，不影响候选补丁、live 文件或索引内容。
- [ ] exact resume 仍未完成。CPU 证据只证明 sampler cursor 可重建，重新设 seed 不能恢复 Python/NumPy/Torch 随机流；多 worker/persistent worker/prefetch 状态仍缺。方案文件 SHA-256 `08AB79948A1462A33EDA5064383D093F8B37FAA566C18ECEE17632947A764E11`；实施前必须单独评审采样协议与预算影响并取得新授权。
- [ ] candidate 仍未部署，未做 GPU、真实跨阶段加载或 live 计划任务验证。先在新对话独立验收当前 Step 1 full 终态；部署、RNG exact-resume、GPU 回归、Step 2/3、正式评估和数据处理继续各自需要明确授权。


## 2026-09-22: Task 12 Step 2 seed0 rerun3 terminal acceptance closure

- [x] New rerun3 run root/task were independently accepted without rerun, stop, or old-root reuse.
- [x] Scheduler/process/status/history/task.log passed: Ready, LastTaskResult=0, no matching process, SUCCESS/0, RESERVED -> RUNNING -> SUCCESS, complete log with no suspicious/nonfinite lines.
- [x] Command/spec and fixed budget passed: batch_size=32, n_accum_steps=1, max_steps=2048, max_val_batches=0, report_every_steps=128, save_every_steps=512, num_workers=0, seed=0; no kernel_gt in command or resolved config; spec kernel_gt is provenance metadata only.
- [x] Endpoint hashes, internal global_step=2048/2049, exact flow_nn/kernel_nn, all tensor/optimizer finiteness, no temporary checkpoint files, and sys.path restoration passed.
- [ ] Step 2 full, other seeds, Step 3, and formal evaluation remain unauthorized and require a new conversation with explicit scope.
