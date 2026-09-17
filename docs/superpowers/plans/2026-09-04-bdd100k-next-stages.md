# BDD100K 后续实验阶段计划（状态更新）

日期：2026-09-05  
状态：训练前工程准入已完成；尚未获得或执行任何 BDD100K pilot、训练、下载、数据处理或恢复。

本文件替代 2026-09-04 的旧状态描述。它记录已经独立核验的工程前置条件和剩余的逐阶段授权边界；不能作为自动启动实验的授权。

## 当前已完成且仍需保持的前置条件

- 数据视图已固定且不重建：clean train/val 为 1565/174，Q2/Q3 noisy train/val 为 926/104；`manifest.csv` SHA-256 为 `6BA1F476AFAEFACA60A9B6EDFB7DB2740BF99D355C12F49335FFB6C342724886`，`summary.json` SHA-256 为 `5E16026E07F54A860298F806123302AAF59C795FBC78ED0ACF9E2B71C9EFDC40`。
- 阶段 A 的 Step 3 完整图像、内部切块、小图边界和输出溯源夹具已经通过。保持 `dataset.test.full_image=true`、`full_test=false`、`inflate_patches=0`、`batch_size=1` 和 `training.require_output_manifest=true`；这不是 DPIR 的真实恢复结论。
- 阶段 B 的 validation-only 运行器成功与失败路径、任务重复拒绝、状态/日志/配置/退出码记录和不覆盖行为已经通过无训练验收。其夹具和序列化样例不是任何后续阶段的前序模型。
- `BaseTrainer` 的终点保存契约已经修复并用无优化夹具回归：完整更新触及 `max_steps` 后强制写入 `training-state-N.pt` 与 `network-snapshot-N.pkl`。`.pt` 的内部 `global_step=N`，对应 `.pkl` 为 `N+1`；不得删除这一路径、增加预算规避终点保存，或把较早的周期文件称为最终产物。

## pilot/full 运行器契约（已实现，仅作无训练验收）

- 新模式只接受 `stage=step1|step2|step3` 和 `mode=pilot|full` 的冻结 JSON spec。运行根必须是新的 `D:\DDM4IP-runtime\experiments` 子目录，拒绝路径穿越、reparse point、既有运行根、重复任务名和重复 execution claim。
- `prepare` 只建立运行根，记录 `RUNNING/awaiting-scheduler`、环境、spec、冻结命令、配置命令和前序工件记录；它不执行项目模块、训练、恢复或下载。pilot/full 的 `direct` 执行被拒绝，实际运行只能由 `start_bdd100k_task.ps1` 创建 Windows 计划任务。
- Step 1 spec 必须声明 `expected_final_global_step`。Step 2/3 spec 必须带完整的上游 `.pt`/`.pkl` 配对路径、各自 SHA-256 和终点 global step；路径限于实验根，文件名、成对目录、哈希、`.pt` 的 `global_step=N`、`.pkl` 的 `global_step=N+1` 以及来源模型键均在预备和执行前再次核验。Step 2 只注入经核验的 `.pt` 到 `models.pretrained_flow.path`；Step 3 只注入经核验的 `.pkl` 到 `models.kernel.path`。
- Step 1/2 成功只有在指定终点的 `.pt` 和 `.pkl` 同时存在、可读、计数相符并含有相应 `flow_nn`/`kernel_nn` 时才成立。Step 3 成功只有在 manifest 行数与 spec 相符、每条记录的源/图块身份唯一、预测图和核文件存在、且 `filter_groups` 具有有效半开 tile/filter 范围时才成立；不假设核数等于图像数。
- 每个任务保留追加 `task.log`、`status-history.jsonl`、原子 `status.json`、`resolved-config.yaml`、冻结命令、`predecessor.json`（如适用）和 `artifacts.json`。原生退出码、运行器退出码和失败 traceback 均不可被 stderr 警告掩盖。

## 下一阶段：仅在新对话中单独授权 Step 1 pilot

启动 Step 1 pilot 前，用户必须在新对话明确确认“只启动 Step 1 pilot”，并在该对话重新完成 AGENTS/WORKLOG、主机、Git 状态、数据视图哈希与当前代码哈希的启动核验。届时应：

1. 审阅并固定 pilot spec 的预算、`expected_final_global_step`、计划任务最长运行时间和唯一任务/运行根名称；不要从本文件推断预算。
2. 通过 `start_bdd100k_task.ps1` 启动一次计划任务，确认一次任务/进程/日志/状态正在更新后停止轮询，并提供状态和日志跟随命令。
3. 用户确认任务结束后，另起核验检查终点配对 checkpoint、内部 global step、SHA-256、冻结配置、日志和退出码；pilot 只用于可运行性和时间/显存估计，不代表模型质量。

Step 2 pilot 仍依赖正式、独立 SHA-256 核验的 Step 1 终点配对；Step 3 真实 GPU 回归仍依赖正式、独立 SHA-256 核验的 Step 2 配对及 D 盘已就绪的 DPIR/DRUNet 权重。每一个 pilot、完整阶段、权重下载和恢复都必须在新的对话中获得单独授权。

## 科学与安全边界

BDD100K 是真实、异质、不配对的直接迁移基线：不报告相对于独立清晰集的 PSNR、SSIM 或 LPIPS；重投影小、锐度上升或 Q2/Q3 筛选均不能单独证明恢复正确或共享 PSF。当前划分不具备来源组隔离证据。远端 Git 继续只读；不得覆盖、删除或重建既有数据视图、实验目录或任务。
