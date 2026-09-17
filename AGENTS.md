# 远端仓库协作规则

本文是 group-pc 代码仓库的补充规则；完整控制规则位于本机控制目录的 AGENTS.md。本文中的“本机”指用户的 Codex 控制机，“远端”指 DESKTOP-KBM1345。

- 实际代码仓库为 group-pc 的 D:\Unsupervised Imaging Inverse Problems。每次新阶段先完整读取本机 AGENTS.md/WORKLOG.md，经 SSH 核验 hostname=DESKTOP-KBM1345，再检查远端 git status 和最新 WORKLOG.md；发现日志差异先说明，以远端新状态为准。
- 项目代码、依赖、数据处理和测试只在已核验远端执行。Git 只读，不提交、推送、拉取、切换分支或配置凭据；保留已有修改。
- 禁止批量/递归删除；只能在授权范围内一次删除一个经过确认的明确文件。禁止覆盖原图、既有数据视图、输出或任务。修改已有文件须核验原始 SHA-256，发生并发修改立即停止。
- 项目 Python 为 E:\Anaconda3\envs\ddm4ip\python.exe；缓存、TEMP/TMP、日志、权重及输出限于 D:\DDM4IP-runtime 项目子目录，只设置进程环境，不修改全局环境。
- 长训练、下载、审计、预处理、评估与 pilot 由 Windows 任务计划程序托管，保存追加日志、配置、独立输出及 RUNNING/SUCCESS/FAILED 状态。启动后只做一次新 SSH 的任务/进程/日志状态确认，提供状态命令及 Get-Content -LiteralPath '<实际日志>' -Tail 50 -Wait 后结束等待；Ctrl+C 仅退出跟随。结果须在用户通知后独立验证。
- synthetic runner 的 SpecPath 是 JSON 文件路径，不是运行目录：start_bdd100k_synthetic_task.ps1 的 prepare 可以读取外部 spec，但 Scheduled Task execute 必须传入 prepare 生成的 <run_root>\spec.json，以保留 runner_sha256 和 reserved_at；不得把外部 spec 原样传给 execute。Task 9 inventory 成功后必须生成 artifacts.json，其中冻结 source_manifest.path、SHA-256、记录数和来源计数；后续 build spec 必须显式传入该 manifest 路径，不能假定 build run root 下自动存在 source-manifest.csv。
- BDD100K pilot/full spec 必须冻结为新的 D:\DDM4IP-runtime\experiments 子目录；Step 2/3 只能注入经独立 SHA-256、文件名、配对终点计数和内部 global step 核验的上游 checkpoint。prepare 只能预备与记录，不能执行项目模块；真实运行只能在用户单独授权的阶段通过 start_bdd100k_task.ps1 创建计划任务，禁止 direct 执行。
- 每次阶段授权以当次用户明确确认的范围为限。运行器验证、每个 pilot、完整训练、权重下载、真实 GPU 恢复与结果复盘各需用户在新对话明确授权；历史计划不构成运行许可。

## Step 3 几何与溯源契约

- BDD100K Step 3 使用 dataset.test.full_image=true、full_test=false、inflate_patches=0、batch_size=1，完整读取 1280×720；不要改 Step 1 的共享 64×64 patch 默认配置。
- loss.patch_size=128、padding=32 表示内部块 160×160，先处理小图右/下扩展，再按既有中心裁边、行优先覆盖拼接，并裁回原图尺寸。几何改动必须测试原始全图、小图和非整除尺寸的逐像素覆盖。
- 保持 Step 2 training.max_val_batches=0；Step 3 need_clean=false、need_noisy=true、training.train=false、save_eval_to_file=true、save_pred_only=true、require_output_manifest=true。
- manifest.jsonl 每张预测一行；源根/相对路径、样本序号、输入/输出尺寸、full_image/tile 标识、tile 坐标、预测/核路径及 solver_geometry 必須齐全。坐标为源像素半开区间 [top,left,bottom,right]。
- solver_geometry.tiles 按行优先排列。filter_groups 中 tile_range/filter_range 为半开范围，明确 shared 或 per_tile；不能以核数等于图像数作为通用假设。已有文件或已记录源图应拒写，失败残留不得自动删除后重试。
- Batch 元数据应兼容 collate、设备迁移和切片，字符串不得调用 .to()。
- 训练前夹具验收只证明数据、几何及保存链路；真实 Step 3 GPU 回归必须使用独立 SHA-256 核验的真实 Step 2 snapshot，以及已缓存的 DPIR/DRUNet 等实际所需权重，不得以恒等夹具替代真实恢复结论。任何首次下载须单独授权，不能混入 pilot。
- 真实数据不配对，不计算相对于独立清晰集的 PSNR/SSIM/LPIPS；重投影小不等于恢复正确，Q2/Q3 不证明共享 PSF，当前划分不能排除相关帧泄漏。

阶段事实、测试退出码、路径/哈希、清理清单、未解决风险与下阶段准入条件写入远端 WORKLOG.md。文件级结果不写成长期规则。


## 运行器夹具、计数与最终保存

- 运行器无训练夹具及检查点序列化样例不是 pilot 或学习产物，不得注入 Step 2/3；验证模式通过不能替代实验模式、前序 SHA-256 注入、最终产物及真实模型加载的验收。
- 当前 global_batch_size=batch_size*world_size*n_accum_steps；global_step/max_steps 和报告/绘图/保存间隔按该批量增量计数。Step 2 full step 包含辅助网络与核更新，不等同于单次 optimizer 调用或全部图像读取张数。
- BaseTrainer.train 保留周期性保存，并在一次完整更新令 global_step >= max_steps 后以 maybe_save_checkpoint(force=True) 强制保存终点。后续改动训练循环时必须用无优化行为回归验证终点同时写出且可从 training-state-N.pt 恢复；不得删除该路径、静默增加预算或把较早文件称为最终 checkpoint。
- 当前 network-snapshot-N.pkl 内部 global_step=N+1，training-state-N.pt 内部为 N；预算核验须联合文件名、对应 .pt 计数、日志、配置和独立 SHA-256。Step 2 读取明确 .pt 的 EMA/flow_nn，Step 3 读取明确 .pkl 的 kernel_nn；禁止自动选未知来源文件。

## Task 11 Step 1 formal b16 fallback rule (2026-09-10)

- The b32 pilot was independently accepted after natural completion: Scheduled Task `DDM4IP-BDD100K-SYNTH-Step1-Pilot-b32` returned `LastTaskResult=0`, `status=SUCCESS`, and produced the verified final checkpoint pair. Its runtime was approximately 3 hours 53 minutes, while the accepted b16 pilot completed the same 64 optimizer updates in approximately 8 minutes 28 seconds.
- For this synthetic benchmark only, the Task 11 Step 1 formal mainline is amended to use `batch_size=16` as a documented fallback. This is an explicit protocol amendment and must not be described as numerically equivalent to the original b32 configuration; gradient statistics, optimization trajectory, and downstream model values may differ.
- Preserve the accepted b32 run root and checkpoint pair as immutable scale/performance reference evidence. The b16 formal run must use a new frozen external spec and a new run root under `D:\DDM4IP-runtime\experiments`; it must not reuse or overwrite the b16 pilot directory.
- Keep the approved synthetic dataset, split, degradation, model, loss, seed, `n_accum_steps`, and evaluation boundaries unchanged unless a later amendment explicitly says otherwise. With one rank and `n_accum_steps=8`, the b16 effective global batch is 128.
- The b16 formal spec must explicitly freeze its budget basis and expected optimizer-update count. Do not copy the b16 pilot `max_steps=8192` by implication: if that gives fewer global samples than the approved full budget, it is a shortened run and must not be called formal full. The spec must record the chosen global-step/sample budget and its derived update count.
- Step 2, Step 3, and formal evaluation remain separately authorized stages. They may consume only the independently verified b16 formal checkpoint when this amended mainline is selected; this documentation change does not start training or authorize downstream stages.
