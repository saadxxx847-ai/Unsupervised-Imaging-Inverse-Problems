## 2026-09-10：Task 11 Step 1 b16 formal fallback 方案 A 已冻结（未授权执行）

### 预算冻结

- 用户在本轮明确选择方案 A。Task 11 Step 1 b16 formal 的冻结合同为 `batch_size=16`、`n_accum_steps=8`、单 rank 有效 global batch=`128`、`max_steps=5242880`、预期 optimizer updates=`40960`。
- 方案 A 保持 parent b32 formal contract 的样本/global-step 总预算；由于 batch size 变化，梯度统计、优化轨迹和最终 checkpoint 仍不得表述为 b32 数值等价结果。
- 方案 B（`max_steps=2621440`、`20480` updates、50% parent sample budget）本轮未选择，不得替代 A 或被混入 formal spec。

### 范围与下一阶段门禁

- b32 pilot run root/checkpoint pair 与 b16 pilot run root/checkpoint pair 继续作为不可覆盖的独立证据保留；b16 formal 必须使用新的 external spec 和新的 run root。
- 本轮只冻结预算和更新文档规则；未创建 formal external spec，未执行 `prepare/execute`，未创建或启动 Scheduled Task，未启动 Step 1 formal、Step 2、Step 3、评估、数据处理或权重下载，未修改项目代码或 benchmark。
- 下一步必须在新对话重新完成启动核验，并由用户明确授权 Task 11 Step 1 b16 formal 执行；执行前仍需按计划复核 benchmark、pilot provenance、runner SHA、路径和目标不存在性，执行后独立验收状态、日志、配置与终点 checkpoint。

## 2026-09-10：Task 11 Step 1 b16 formal fallback 预算评审完成（正式预算未冻结）

### 本轮范围与新鲜核验

- 本轮按 `AGENTS.md` 完成启动核验，并完整读取远端最新 `WORKLOG.md`、原始 synthetic design/spec、原 Task 11 实施计划、b16 formal fallback amendment 与 fallback plan。远端主机为 `DESKTOP-KBM1345`，仓库为 `D:\Unsupervised Imaging Inverse Problems`，分支为 `main`；既有 dirty worktree 和未跟踪文件全部保留，未执行 Git 写操作。
- b16 pilot 的既有独立验收记录为 `SUCCESS/0`、64 次 optimizer updates、约 8 分 28 秒；b32 pilot 本轮新鲜只读检查到 `status.json=SUCCESS/exit_code=0`、Scheduled Task `LastTaskResult=0`、终点 `training-state-16384.pt` 与 `network-snapshot-16384.pkl` 均存在。b32 运行根和 checkpoint pair 保持不可覆盖。
- 远端 `WORKLOG.md` 顶部旧条目仍停留在“b32 启动、终态待独立验收”的历史记录，尚未补写与 b32 独立终态验收对应的收尾条目；本轮保留该证据差异，不把单个 `SUCCESS` 或 `LastTaskResult=0` 单独升级为完整 b32 终态验收结论。
- 本轮只完成预算比较和规则补充：未创建正式 external spec，未执行 `prepare/execute`，未创建或启动 Scheduled Task，未启动训练、Step 2、Step 3、评估、数据处理或权重下载，未修改项目代码或 benchmark。

### b16 正式预算比较

- 有效 global batch 按 `batch_size=16`、单 rank、`n_accum_steps=8` 计算为 `128`。
- 方案 A（sample/global-step preserving）：`max_steps=5242880`，`5242880/128=40960` 次 optimizer updates，总样本/global-step 预算与 parent b32 formal contract 相同；按 b16 pilot 线性外推约 `90` 小时。
- 方案 B（optimizer-update preserving）：`max_steps=2621440`，`2621440/128=20480` 次 optimizer updates，与 parent b32 的 optimizer-update 数相同，但样本预算为其 `50%`；按 b16 pilot 线性外推约 `45` 小时，必须标记为 `budget-reduced fallback`。
- b16 pilot 的 `max_steps=8192` 仅对应 `64` 次 optimizer updates，继续保持 pilot 身份，不能称 formal full。以上耗时只是规划外推，正式运行还可能受到 checkpoint、绘图和系统吞吐波动影响。

### 评审结论与下一准入

- 当前建议：若研究可比性和完整样本预算优先，选择 A；若报告期限使约 90 小时不可接受，选择 B。两者都不能表述为原始 b32 配置的数值等价结果。
- 预算必须由用户明确选择 A 或 B 后才算冻结；推荐、amendment 文档或 pilot 通过均不构成预算选择或执行授权。选择后仍需单独明确授权 Step 1 formal 执行，并使用新的 external spec、run root 与 Scheduled Task 路径。
- 报告必须写明 `batch_size=16`、有效 global batch、`max_steps`、optimizer-update 数和预算 basis；A 应表述为 documented b16 fallback 的 sample/global-step-preserving 方案，B 应表述为 optimizer-update-preserving、50% parent sample budget 的 budget-reduced fallback。

## 2026-09-10：Task 11 Step 1 b32 pilot 已通过 Scheduled Task 启动，终态待独立验收

### 启动核验与授权范围

- 本轮按 `AGENTS.md` 完成完整启动核验；`ssh group-pc` 主机为 `DESKTOP-KBM1345`，远端仓库为 `D:\Unsupervised Imaging Inverse Problems`，分支为 `main`。远端既有 dirty worktree 和未跟踪文件全部保留，未执行 Git 写操作。
- 完整读取本机与远端最新 `WORKLOG.md`、已批准设计、原实施计划和 canonical remediation plan。b01、b02、b04、b08、b16 已有独立终态通过证据；本轮只授权 b32 pilot，不授权 Step 1 full、Step 2、Step 3 或正式评估。
- 启动前新鲜核对 b16 为 `Ready/LastTaskResult=0/SUCCESS/0`；b32 目标 task/run root/reserved spec 均不存在；Step 1 full、Step 2、Step 3 相关任务与匹配进程数均为 `0`。benchmark 输入和当前 runner SHA-256 与既有合同一致。

### b32 external spec 与唯一启动入口

- 用户指定的全新 external spec 在启动前尚未落地；本轮按固定合同新建 `D:\DDM4IP-runtime\experiments\phaseD-step1-pilot-spec-20260910-b32.json`，创建前确认目标不存在，创建后字节数为 `1201`，SHA-256=`957CC1B11591D74DF82981FC62846C50EEFE3986FE33CE4B1FE14CB60EE205FE`。
- spec 固定 `stage=step1`、`mode=pilot`、`variant=null`、`expected_manifest_records=1000`；overrides 为 `training.batch_size=32`、`training.max_steps=16384`、`loss.n_accum_steps=8`，global batch size=`256`，对应 `64` 次 optimizer updates。
- run root：`D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-pilot-b32`；Scheduled Task：`DDM4IP-BDD100K-SYNTH-Step1-Pilot-b32`。
- 仅通过 `D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1` 注册并启动；launcher 退出码为 `0`。Scheduled Task execute 使用 prepare 生成的 `<run_root>\spec.json`，没有把 external spec 直接传给 execute。

### 启动后唯一存在性快照与边界

- 任务对象存在，状态为 `Running`，`LastTaskResult=267009 (0x41301)`；匹配 b32 项目的进程数为 `3`。
- run root、`status.json`、`status-history.jsonl` 和 `task.log` 均存在。本轮没有读取这些文件内容，没有判断 `SUCCESS/FAILED`，没有持续轮询、重启或重跑。
- 未启动 Step 1 full、Step 2、Step 3 或正式评估；未下载权重、修改代码、修改 benchmark 或删除历史证据。b32 终态必须在用户新对话中重新授权后独立核对 scheduler、进程、status/history、完整 task.log、终点 checkpoint pair、SHA-256、内部 `N/N+1`、`flow_nn`、全量张量有限性和显存门；b32 通过后 Step 1 full 仍需另一个新对话单独授权。
# 工作日志

## 2026-09-10：Task 11 Step 1 b16 独立终态验收通过

### 新鲜只读交叉核验

- 本轮只做 b16 的新鲜只读终态验收；未重启或重跑 b16，未修改 b08，未启动 b32、Step 1 full、Step 2、Step 3 或正式评估。
- 通过新的 SSH 进程核验远端主机为 DESKTOP-KBM1345；b16 Scheduled Task 对象存在且为 Ready，LastTaskResult=0，NumberOfMissedRuns=0，LastRunTime=2026-09-10T09:42:45+08:00；匹配 b16 运行根/spec 的项目进程数为 0。
- Scheduled Task action 为 run_bdd100k_synthetic_stage.ps1 -Action execute -SpecPath D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-pilot-b16\spec.json；execute 使用 prepare 生成的 reserved spec，没有把 external spec 直接传给 execute。
- b32、Step 1 full、Step 2、Step 3 相关 Scheduled Task 数为 0，匹配禁止阶段的项目进程数为 0。

### b16 规格与状态/日志工件

- external spec：D:\DDM4IP-runtime\experiments\phaseD-step1-pilot-spec-20260909-b16.json，SHA-256=F873C8529ECC4B561A62900EB73B1A533BC3FF9EDC6C846ED8525C630E88E847。
- run root：D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-pilot-b16；Scheduled Task：DDM4IP-BDD100K-SYNTH-Step1-Pilot-b16。
- reserved spec.json 为 1287 字节，SHA-256=821599165EBE87DDBDCDF928BB50833891B6B12B60E5C385990CB4923BDC17AC；external/reserved 的 run_root、task_name 和 overrides 完全一致，reserved_at 存在。
- 固定 overrides 为 training.batch_size=16、training.max_steps=8192、loss.n_accum_steps=8；global batch size=128，对应 64 次 optimizer updates；stage=step1、mode=pilot、variant=null、expected_manifest_records=1000。
- status.json 为 SUCCESS、exit_code=0，457 字节，SHA-256=E414686780685516E035C3064163E5AFE416936E0D2CBB89C45392B62CD6EF29。
- status-history.jsonl 为 953 字节，SHA-256=2335B921C4E9945626A0FF54EF474A153A574EC0CC302975961697CD0E6C5EB6；按完整 JSON 对象边界解析为严格 RESERVED -> RUNNING -> SUCCESS，共 3 个对象、1 个终态、无重复终态。
- 完整 task.log 为 8071 字节，SHA-256=54B0A40305094F254EDB085DFC3648B179F68FBE696769C9E22368946809B1A6；含 Training finished at step 8192、Saved checkpoint、Saved network snapshot 和 execution finished: status=SUCCESS exit_code=0；独立词边界检查未发现 NaN/Inf/Infinity/nonfinite。

### 终点 checkpoint 独立验收

- training-state-8192.pt 为 67265000 字节，SHA-256=C65555B401385D7CFD92080A0716A5434C45C05B1A1F165DB81CC0138664F5C2；远端 E:\Anaconda3\envs\ddm4ip\python.exe 只读加载后内部 global_step=8192，含 flow_nn，递归发现 519 个张量且全部有限。
- network-snapshot-8192.pkl 为 16862877 字节，SHA-256=15E1D646A4E8E170C2888F33B9B9CAE143534B72BE77C68445E052A3AA6D701E；只读加载后内部 global_step=8193，含 flow_nn=RFNoPrecond，105 个模型 state 张量全部有限。pickle 加载前确认仓库根不在 sys.path，临时加入后已恢复原路径。
- 新独立审计脚本 D:\DDM4IP-runtime\temp\b16-independent-audit-20260910.py 为 6606 字节，SHA-256=1B5D6898CC9BDD19873642429263099A817E5672198A99CD96104643EE9B1E77，退出码为 0，结果为 AUDIT_RESULT PASS；其 PYTHONPYCACHEPREFIX 位于 D:\DDM4IP-runtime\temp\b16-independent-audit-20260910-pycache。

### 结论与下一准入

- 结论：b16 已通过 Task 11 Step 1 pilot 的独立 scheduler/执行/工件终态门。SUCCESS、launcher 退出码或单个子进程退出码均未被单独作为依据；本轮同时核对了任务状态/LastTaskResult、reserved execute spec、进程、status、对象边界 history、完整 task.log、SHA-256、内部 8192/8193、flow_nn 和全量张量有限性。
- 下一准入仅为新的对话中用户明确授权 Task 11 Step 1 的 b32 pilot；b32 固定为 batch_size=32、max_steps=16384、n_accum_steps=8、global batch size=256、64 次 optimizer updates。b32 必须使用全新的 external spec、Scheduled Task 和 run root，并再次独立验收显存/终态工件门；b32 通过后 Step 1 full 仍需另一个新对话单独授权。
- 本轮没有修改代码、benchmark 或既有历史证据，没有删除任何文件；b16 run root、任务、spec、状态、日志、checkpoint 和独立审计辅助文件均保留。

### 清理清单增量

- D:\DDM4IP-runtime\experiments\phaseD-step1-pilot-spec-20260909-b16.json、D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-pilot-b16、DDM4IP-BDD100K-SYNTH-Step1-Pilot-b16、D:\DDM4IP-runtime\temp\b16-independent-audit-20260910.py 及其 PYTHONPYCACHEPREFIX 目录为本项目专用 b16 证据，当前保留；清理时只允许按精确路径处理，不得递归删除。


## 2026-09-10：Task 11 Step 1 b16 已通过 Scheduled Task 启动，终态待独立验收

### 启动核验与授权范围

- 本轮只授权 Task 11 Step 1 的 b16 pilot；未授权 b32、Step 1 full、Step 2、Step 3 或正式评估，也未重启或重跑 b08。
- 本机主机为 zzz，通过 ssh group-pc 核验远端主机为 DESKTOP-KBM1345；远端仓库为 D:\Unsupervised Imaging Inverse Problems，分支为 main。既有 dirty worktree 和未跟踪文件全部保留，未执行 Git 写操作。
- 启动前新鲜核对 b08：Scheduled Task 为 Ready、LastTaskResult=0、状态文件为 SUCCESS/0，终点 checkpoint pair 和三份状态/日志文件均存在；b16 external spec、run root、task 均不存在，b32/Step 1 full/Step 2/Step 3 相关任务不存在，匹配项目进程数为 0。

### b16 规格与唯一启动入口

- external spec：D:\DDM4IP-runtime\experiments\phaseD-step1-pilot-spec-20260909-b16.json，SHA-256=F873C8529ECC4B561A62900EB73B1A533BC3FF9EDC6C846ED8525C630E88E847。字段沿用已核验 Step 1 pilot 合同：stage=step1、mode=pilot、variant=null、expected_manifest_records=1000；overrides 为 training.batch_size=16、training.max_steps=8192、loss.n_accum_steps=8。
- run root：D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-pilot-b16；Scheduled Task：DDM4IP-BDD100K-SYNTH-Step1-Pilot-b16。global batch size=128，对应 64 次 optimizer updates。
- 仅调用 D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1 注册并启动；launcher SSH/远端退出码为 0。未 direct 执行 runner、stage wrapper 或训练模块；launcher 的 execute 合同使用 prepare 生成的 <run_root>\spec.json。

### 启动后唯一存在性快照

- 任务对象存在；任务状态为 Running；LastTaskResult=267009（0x41301，表示仍在运行）；匹配 b16 项目进程数为 3。
- run root 存在；status.json、status-history.jsonl 和 task.log 均存在。
- 本轮没有读取上述文件内容，没有判断 b16 的 SUCCESS/FAILED，没有持续轮询、重启或重跑；未启动 b32、Step 1 full、Step 2、Step 3 或正式评估。

### 下一准入与清理清单

- b16 当前只记录为“已由 Scheduled Task 托管，终态待后续独立验收”。用户确认其终态后，必须在新的对话中重新授权并按 scheduler、进程、status/history、完整 task.log、终点 checkpoint pair、SHA-256、内部 N/N+1、flow_nn 和全量张量有限性独立验收；在此之前不得进入 b32 或 Step 1 full。
- 新 external spec、b16 run root、Scheduled Task 及其状态/日志/检查点属于本项目专用证据，均保留；本轮未删除历史证据、benchmark 或代码。

## 2026-09-10：Task 11 Step 1 b08 独立终态验收通过

### 新鲜只读交叉核验

- 本轮只做 b08 的新鲜只读终态验收；未重启或重跑 b08，未启动 b16、b32、Step 1 full、Step 2、Step 3 或正式评估。
- DDM4IP-BDD100K-SYNTH-Step1-Pilot-b08 为 Ready，LastTaskResult=0，NumberOfMissedRuns=0，匹配 b08 的进程数为 0。Scheduled Task action 使用 run_bdd100k_synthetic_stage.ps1 -Action execute -SpecPath D:\DDM4IP-runtime\experimentsdd100k-synthetic-motionblur-v1-step1-pilot-b08\spec.json，未把 external spec 直接传给 execute；未发现 b16、b32、Step 1 full、Step 2 或 Step 3 的任务/进程。
- external spec D:\DDM4IP-runtime\experiments\phaseD-step1-pilot-spec-20260909-b08.json SHA-256=E72568DB0BFAF23A59AEE7A586C0CF1745A45B0989A8640C080EE976A5A473FC；reserved spec.json SHA-256=0F7BED952E8671A0AD6D5F9444CFA1059EEEE1261F340CB67A3CE4D9AE0B774A。两者均绑定 run root D:\DDM4IP-runtime\experimentsdd100k-synthetic-motionblur-v1-step1-pilot-b08，overrides 为 training.batch_size=8、training.max_steps=4096、loss.n_accum_steps=8；global batch size=64，对应 64 次 optimizer updates。
- status.json 为 SUCCESS/0，SHA-256=CAAE847FF1F2710518109611A9290088BAF874891C2C4EE8788C2944C41ABED5；完整 status-history.jsonl 按 JSON 对象边界解析为严格 RESERVED -> RUNNING -> SUCCESS，共 3 个对象、1 个终态、无重复终态，SHA-256=C39BF6D7A3C92D1FE261F42BA04ACBFE28918A8EE1510190B3BCE81316AEB6EB。
- 完整 task.log 为 8037 字节，SHA-256=61B61AAA68BC9FD146764BAB17E926455204483DD72674006B09D3698B8BFE14；包含 Training finished at step 4096、终点 checkpoint/network snapshot 保存和 execution finished: status=SUCCESS exit_code=0，独立词边界检查未发现 NaN/Inf/Infinity/nonfinite。
- 终点 pair 均存在：training-state-4096.pt 为 67265000 字节、SHA-256=D48BACDDF15E2DFA9496850A0BB81D7766841A209C36A3D048ED82DA419CA9D4；network-snapshot-4096.pkl 为 16862877 字节、SHA-256=53339BCEE6716034CDA6D405C8F98BA33678D0F248D590173A7D5C18ACE6CCC7。
- 使用远端 E:\Anaconda3\envs\ddm4ip\python.exe 独立加载 checkpoint：.pt 内部 global_step=4096，含 flow_nn，递归发现 519 个张量且全部有限；.pkl 内部 global_step=4097，含 flow_nn=RFNoPrecond，模型 state dict 的 105 个张量全部有限。pickle 加载前确认仓库根不在 sys.path，临时加入后已恢复原路径；独立审计脚本 v2 SHA-256=e6359b1a3af70f3734194c13fc6953a0ba1b9928c5368113eb59d8d886260864，退出码为 0、AUDIT_RESULT PASS。

### 结论与下一准入

- 结论：b08 已通过 Task 11 Step 1 pilot 的独立 scheduler/执行/工件门。下一准入仅为新对话中用户明确授权的 b16；b16 通过后才可申请 b32，b32 通过且满足显存/有限性门后仍需另一个新对话单独授权 Step 1 full。

### 清理清单增量

- D:\DDM4IP-runtime	emp08-independent-audit-20260910.py、D:\DDM4IP-runtime	emp08-independent-audit-20260910-v2.py 及 v2 运行产生的 pycache 目录为本项目独占的只读验收辅助文件，未删除；清理时按精确路径处理。



## 2026-09-09：Task 11 Step 1 b08 启动证据（终态待独立验收）

### 授权范围与启动核验

- 本轮只授权 Task 11 Step 1 的 b08 pilot；未启动 b16、b32、Step 1 full、Step 2、Step 3 或正式评估。b01、b02、b04 的成功证据和其他历史运行根均保留，未覆盖或删除。
- 已按 AGENTS.md 完成启动核验：远端主机为 DESKTOP-KBM1345，仓库为 D:\Unsupervised Imaging Inverse Problems、分支为 main；既有 dirty worktree 和未跟踪文件全部保留，未执行 Git 写操作。
- 启动前确认 b08 external spec、Scheduled Task、run root 和 reserved spec.json 均不存在；b01、b02、b04 的既有 task/run root 未复用。

### b08 规格与调度证据

- external spec：D:\DDM4IP-runtime\experiments\phaseD-step1-pilot-spec-20260909-b08.json，SHA-256=E72568DB0BFAF23A59AEE7A586C0CF1745A45B0989A8640C080EE976A5A473FC，字段固定为 stage=step1、mode=pilot、variant=null；overrides 为 training.batch_size=8、training.max_steps=4096、loss.n_accum_steps=8。
- run root：D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-pilot-b08；Scheduled Task：DDM4IP-BDD100K-SYNTH-Step1-Pilot-b08。按计划 global batch size 为 64，对应本 pilot 的 64 次 optimizer updates；不把 max_steps 解释为 optimizer update 数。
- 唯一实际启动入口为 D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1，调用 launcher 退出码为 0；没有 direct 执行 runner、stage wrapper 或训练模块。launcher 内部 prepare 生成 reserved spec 后，Scheduled Task action 已独立核对为使用 <run_root>\spec.json，不是 external spec。
- 第一次外层 SSH 调用因本地包装脚本解析失败而未进入 launcher，且未留下 task/run root；随后使用同一 launcher 的最小调用成功。该诊断不改变 b08 spec，也未覆盖任何历史证据。

### 启动后一次性存在性快照与边界

- 启动后的唯一快照：task 存在且为 Running，LastTaskResult=267009（0x41301，表示仍在运行）；匹配 b08 的进程数为 3；run root、status.json、status-history.jsonl 和 task.log 均存在。按本轮授权未读取这些文件内容、未判断 SUCCESS/FAILED、未持续轮询或做终态验收。
- 下一步只能在用户新对话中明确授权后，对 b08 做一次独立终态验收（含 scheduler、进程、status/history、完整 task.log、checkpoint pair、SHA-256、内部 N/N+1、flow_nn 和全量张量有限性）；在该验收完成前不得启动 b16，也不得进入 Step 1 full、Step 2、Step 3 或正式评估。

## 2026-09-09：Task 11 Step 1 b04 独立终态验收通过

### 新鲜只读交叉核验

- 本轮仅做 b04 的独立终态验收；未重启或修改 b04，未启动 b08、b16、b32、Step 1 full、Step 2、Step 3 或正式评估。远端主机为 DESKTOP-KBM1345；任务、run root、状态文件、历史、日志和 checkpoint 均在远端 group-pc 上核对。
- Scheduled Task DDM4IP-BDD100K-SYNTH-Step1-Pilot-b04 为 Ready，LastTaskResult=0，NumberOfMissedRuns=0，匹配 b04 的进程数为 0；独立检查未发现 b08、b16、b32、Step 1 full、Step 2 或 Step 3 的任务/进程。
- external spec D:\DDM4IP-runtime\experiments\phaseD-step1-pilot-spec-20260909-b04.json SHA-256=30B865B3118A0F3A20EF10D4EC4C220E63665BA0887B69DA02219DA358AF4E1C；reserved spec.json SHA-256=05122FFDC0753372F3FAE616729BF927FB94DBEDAA77EEE7710974A7BBCCE6D6。两者均绑定 run root D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-pilot-b04，实际 overrides 为 training.batch_size=4、training.max_steps=2048、loss.n_accum_steps=8；stage=step1、mode=pilot、variant 为 null。

### 终态与工件

- status.json 为 SUCCESS、exit_code=0，SHA-256=AB80B9ED1A53833CC81B9805668266B18F364501B3C9FD0F11C71D699ACA39F6；status-history.jsonl 按 JSON 对象边界完整解析为严格 RESERVED -> RUNNING -> SUCCESS，共 3 个对象、1 个终态、无重复终态，SHA-256=A3144858B0B547CADFFA6EC0A62A46F1D2D9F693A1B6F9FFB3E7BFC20B0EE72C。
- 完整读取 task.log：8037 字节，SHA-256=302652D7D4B0CA8A5B107CB3D703D8B5B676CF495A34287C9BBEF75DDD0EEFC6；包含 Training finished at step 2048、终点 checkpoint/network snapshot 保存和 execution finished: status=SUCCESS exit_code=0，未发现独立词边界 NaN/Inf/Infinity/nonfinite。
- 终点 pair 均存在：training-state-2048.pt 为 67265000 字节、SHA-256=9137369313B2FFB2FD78C7C408F8D860CCD345DD30BC9218864E0525251C4B36；network-snapshot-2048.pkl 为 16862877 字节、SHA-256=4C4B47A0E84877562A3ABED4023034D68844E887A213FC29CF92D8604EC58B9B。
- 使用远端 E:\Anaconda3\envs\ddm4ip\python.exe（PyTorch 2.4.1+cu118）只读加载 checkpoint：.pt 内部 global_step=2048，含 flow_nn，519 个张量全部有限；.pkl 内部 global_step=2049，含 flow_nn=RFNoPrecond，105 个模型张量全部有限。pickle 加载期间临时加入仓库根 sys.path，返回后已恢复原路径。

### 结论与下一准入

- 结论：b04 已通过 Task 11 Step 1 pilot 的独立执行/工件门；本轮没有把单一退出码或 SUCCESS 单独当作依据，而是同时核对了 scheduler、进程、spec、status、对象边界 history、完整日志、SHA-256、内部 N/N+1、flow_nn 和全量张量有限性。
- 下一步只能在新对话中由用户明确授权 b08（batch_size=8、max_steps=4096、n_accum_steps=8），并创建全新 external spec、Scheduled Task 和 run root；b16、b32 仍须按顺序逐个授权和验收，b32 通过前不得进入 Step 1 full。

## 2026-09-09：Task 11 Step 1 b04 已通过 Scheduled Task 启动，终态待独立验收

### 授权范围与启动核验

- 本轮只授权 Task 11 Step 1 的 b04 pilot；未授权 b08、b16、b32、Step 1 full、Step 2、Step 3 或正式评估。b01、b02 的独立终态证据和其他历史运行根均保留，未覆盖。
- 已按 AGENTS.md 完成启动核验：ssh group-pc hostname 为 DESKTOP-KBM1345；远端仓库为 D:\Unsupervised Imaging Inverse Problems、分支为 main；既有 dirty worktree 和未跟踪文件全部保留，未执行 Git 写操作。
- 已完整读取本机与远端最新 WORKLOG.md 及 canonical remediation plan；远端日志和计划与 b04 的当前准入顺序一致。

### b04 规格与启动证据

- external spec：D:\DDM4IP-runtime\experiments\phaseD-step1-pilot-spec-20260909-b04.json，SHA-256=30B865B3118A0F3A20EF10D4EC4C220E63665BA0887B69DA02219DA358AF4E1C。
- run root：D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-pilot-b04；Scheduled Task：DDM4IP-BDD100K-SYNTH-Step1-Pilot-b04。
- 固定 overrides：training.batch_size=4、training.max_steps=2048、loss.n_accum_steps=8；本条不把 max_steps 解释为 optimizer update 数。
- 只通过 D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1 注册并启动；launcher 退出码为 0，没有 direct 执行 runner 或训练模块。
- 启动后只做了一次存在性快照：任务对象存在，LastTaskResult=267009 (0x41301)，匹配 b04 的进程数为 3；status.json、status-history.jsonl 和 task.log 均存在。按本轮授权未读取这些文件内容、未判断 SUCCESS/FAILED、未持续轮询。

### 下一准入

- b04 的终态已在本日志顶部的独立验收记录中通过；下一步只能在用户新对话中明确授权后进入 b08，不能据此自动启动 b16、b32、Step 1 full、Step 2、Step 3 或正式评估。


## 2026-09-09：Phase C Oracle GPU pilot v6 独立验收通过，Task 10 关闭

### 结论与范围

- 按用户授权完成 Phase C：只使用已冻结 benchmark 与 D 盘离线权重，未训练、未运行正式 500 图评估、未进入 Task 11。
- v1–v5 的失败运行根、spec、状态历史、日志和部分工件均保留；没有覆盖、删除或改写历史证据。
- v6 是首个通过完整独立验收的 Oracle 16 图 pilot。技术门已关闭；Task 11 仍需用户在新对话中单独明确授权。

### v6 运行与调度证据

- 任务：DDM4IP-BDD100K-SYNTH-Oracle-Pilot-v6；主机：DESKTOP-KBM1345；Python：E:\\Anaconda3\\envs\\ddm4ip\\python.exe。
- external spec：D:\\DDM4IP-runtime\\experiments\\phaseC-oracle-pilot-spec-20260909-v6.json，SHA-256=`569DCF1A030515A2903BE00FEF48783109DA061FCB29C79F38875A867CEFAAF7`；reserved spec：D:\\DDM4IP-runtime\\experiments\\bdd100k-synthetic-motionblur-v1-oracle-pilot-v6\\spec.json，SHA-256=`618D6ED31BFED67C453B1D557282454ECB5FEE52BB67B5CD41C3B8106FFE07F6`。
- run root：D:\\DDM4IP-runtime\\experiments\\bdd100k-synthetic-motionblur-v1-oracle-pilot-v6；task.log：D:\\DDM4IP-runtime\\experiments\\bdd100k-synthetic-motionblur-v1-oracle-pilot-v6\\task.log，SHA-256=`8F972AF6830F2AA4ED2D59C1BCD20E7B7F9C2331A3B608B64E0A7A5A7305E3EA`。
- status.json 为 `SUCCESS`、exit_code=`0`，SHA-256=`49DBA3884D07923EAA803DDCEB8C86A817D4084353E95243D22E66E76D662B1E`；Windows Task Scheduler `LastTaskResult=0`、无 missed run、无残留 v6 进程。
- status-history.jsonl SHA-256=`383CEBB809AC7BE80C176B31802DE1D51458234AF0F67C802A3F1D95F07A271F`，完整且无重复：`RESERVED -> RUNNING -> SUCCESS`。

### 根因修复与无训练门禁

- v5 的 `physics.A_adjoint` 0×0 filter 根因已由实际 filter 追踪定位：Oracle 的 `kernel_nn` 与可变 `physics` 对象发生别名；每个 batch 的 crop/update 会把 32×32 filter 继续缩小，最终传入 0×0。`ddm4ip/trainers/deepinv_denoiser.py` 以 `copy.deepcopy(kernel_nn)` 隔离冻结 kernel 与可变 solver physics；修复后文件 SHA-256=`9CDBA7D6DD4275E39E7E6AE2C988D349767103632AA60D30F5361E41DC3BBCCE`。
- 真实 RED：`D:\\DDM4IP-runtime\\temp\\phaseC-oracle-filter-red-20260909\\red.log`，退出码 `1`；真实 GREEN：`D:\\DDM4IP-runtime\\temp\\phaseC-oracle-filter-green-20260909\\green.log`，退出码 `0`。
- 修复后 focused no-training 回归 `40/40`、退出码 `0`；完整 `unittest discover` `70/70`、退出码 `0`；四个 synthetic Hydra `--cfg job --resolve` 均退出码 `0`。
- `HF_HUB_OFFLINE=1`、`TRANSFORMERS_OFFLINE=1` 网络守卫下实际构造 LPIPS AlexNet、DRUNet、DPIR 通过，network guard hits=`0`；benchmark summary/dev pairs/kernel 哈希门通过。

### v6 独立工件验收

- `plots` 中 prediction=`16`、kernel=`16`、manifest=`1`、metrics=`1`、summary=`1`；16 个 source_id 唯一，PNG 为 256×256 RGB。
- summary.json SHA-256=`597EBD8F99E71FCA72C7E0572F71D8AF88F2076F771DC2CD1823277709208216`；manifest.jsonl SHA-256=`096F7B02970723851D737B2F7B486B57311ABC834BA843D2D71665323C0B1903`；metrics.jsonl SHA-256=`28A99AAFF83EF29593E03EE8370F98CAD6D4D595B72F268FAF7375C935A60F87`。
- 独立审计脚本 `D:\\DDM4IP-runtime\\temp\\phaseC-v6-independent-audit-20260909-v2.py` SHA-256=`7AA4233AF1720DDDED3C75B53012D43CFA4DAF3BA3FA2478AD48472250A39C1E`，退出码 `0`，结果 `PASS`；审计重新读取 JSONL、PNG 和 kernel 文件并逐项复核 SHA-256。
- 16 个 kernel 均为 `1×1×30×30`，有限、非负、归一化，sum=`0.9999990463256836`；所有指标有限，manifest/metrics/summary 哈希链一致。
- input 均值：PSNR=`19.537445425987244`、SSIM=`0.399074824526906`、LPIPS=`0.6320396475493908`；restored 均值：PSNR=`26.53449785709381`、SSIM=`0.8099273145198822`、LPIPS=`0.23762223310768604`。三项方向均满足 Oracle 改善要求。

### 阶段结论与下一准入

- Phase C / Task 10 Oracle GPU pilot 正式关闭。Task 11 Step 1 pilot 尚未启动、尚未授权；不自动进入 full training。
- 下一阶段必须在新对话中单独授权 Task 11 Step 1 pilots，按 `b01 -> b02 -> b04 -> b08 -> b16 -> b32` 顺序、每次新 task/run root、每次独立验收；b32 通过前不得进入 Step 1 full。
- 新增 v6 证据路径均为项目专用并保留：external/reserved spec、v6 run root、task.log、status/history、v6 独立审计脚本及本条引用的 RED/GREEN 与无训练门禁日志。未执行清理。

## 2026-09-08：Phase C Oracle GPU pilot v2 在 GPU 前置哈希门失败，未产出评估结果

### 启动前新鲜门禁

- 本轮按 `AGENTS.md` 完成启动核验：`ssh group-pc hostname` 为 `DESKTOP-KBM1345`，远端仓库为 `D:\Unsupervised Imaging Inverse Problems`，分支为 `main`；既有 dirty worktree、未跟踪文件和旧失败运行根均保留，未执行 Git 写操作。
- 已完整读取用户附上的 `2026-09-08-BDD100K-Task10-修正与后续执行总计划.md`、批准设计和原实施计划；本轮用户授权仅覆盖 Phase C Oracle GPU pilot，不覆盖代码修复、训练、正式 500 图评估或删除历史证据。
- 新鲜离线门禁在 `D:\DDM4IP-runtime\temp\phaseC-preflight-20260908-v4\offline-result.json` 通过：LPIPS AlexNet、DRUNet、DPIR 实际构造成功，AlexNet SHA-256=`7be5be791159472b1fbf3c69796f7cb30dca7ad8466c2df70058c37116cdee02`，DRUNet SHA-256=`20296845d272d3d786b89ea3c1208d5f2ceb57658a499d4dd28073cbb73508aa`，`HF_HUB_OFFLINE=1`、`TRANSFORMERS_OFFLINE=1`、`network_guard_hits=0`，临时/缓存路径均为 D 盘。
- 在正确仓库目录重新运行完整无训练回归：`Ran 67 tests in 15.306s`、`OK`、退出码 `0`；日志为 `D:\DDM4IP-runtime\temp\phaseC-preflight-20260908-v4\unittest-from-repo.log`。此前一次从错误工作目录运行的 `ImportError: Start directory is not importable: 'tests'` 仅作为诊断证据保留，不是代码失败。

### v2 启动与独立失败验收

- 冻结 spec `D:\DDM4IP-runtime\experiments\phaseC-oracle-pilot-spec-20260908-v2.json` 的 SHA-256=`5340F3F9C166282484E0A8D21DC9BF882E5C99CA82B157E27DE8ED2960DDDF42`；当前 runner SHA-256=`9ED9344827D11A051AD60416A4E9F8085A9026D89105C15E48F76510CE4C8710`。v1 失败 spec/run root 未复用。
- 通过唯一 launcher 创建并启动 `DDM4IP-BDD100K-SYNTH-Oracle-Pilot-v2`，run root 为 `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot-v2`；launcher 退出码 `0`。独立验收得到任务 `Ready`、`LastTaskResult=1`，状态历史严格为 `RESERVED -> RUNNING -> FAILED`，无重复触发。
- v2 `status.json` 为 `FAILED`、`exit_code=1`；`status.json` SHA-256=`065FCFE5900AF8FEC0218B0923541511ADA294EA5443B2CEFFA551FEBD960934`，`status-history.jsonl` SHA-256=`F291611327435387349D16C93EACF39238A7168F5B236217DC0A8976DE5DF1E5`，`task.log` SHA-256=`5022A52314637F0F37DCF13BBC2C992B9E41C81E4B385568AADAECA2820FF66C`。
- 失败发生在 `ddm4ip/trainers/deepinv_denoiser.py:317` 的 `configured kernel_gt_sha256 does not match kernel_gt_path`；`plots` 目录存在但 prediction 数量 `0`、kernel 数量 `0`、`summary.json` 不存在，故本轮没有可验收的 16 图 Oracle 结果，也不能标记 Phase C 或 Task 10 通过。

### 根因与边界

- 实际 `kernel-gt.pt` SHA-256 为大写显示的 `4E292CA42C026965EF9B6D16CACEC83091DFC2E461C2C6788C6FDC690F832A7A`，Python `hashlib.hexdigest()` 返回同值的小写形式；runner 对 benchmark preflight 已使用大小写不敏感比较，但 trainer 的 kernel claim 比较仍为大小写敏感：`self.metric_writer.kernel_gt_sha256 != claimed_kernel_hash`。因此 v2 在数据迭代和工件写出前失败。这是当前 Phase A 修正链遗漏的 hash canonicalization 回归，不是 benchmark、权重或数据缺失。
- 本轮未修改代码、未修改 benchmark、未覆盖/删除 v1 或 v2 运行根，也未启动训练或正式 500 图评估。Phase C 停在前置代码缺陷，下一准入是新对话中用户单独授权最小 Phase A hash canonicalization 修正与回归；修正通过后再以新的 v3 task/run root 重新授权 Phase C，不得复用 v2 失败根。

### 清理清单增量

- `D:\DDM4IP-runtime\experiments\phaseC-oracle-pilot-spec-20260908-v2.json`：v2 冻结 spec，本项目独占，保留。
- `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot-v2`：失败 Oracle 运行根，含状态、历史、日志、Hydra 配置和空 `plots`，保留为诊断证据。
- `D:\DDM4IP-runtime\temp\phaseC-preflight-20260908-v4`：离线门禁与 67 测试日志，本项目独占，未删除。

## 2026-09-08：Phase A 最小路径契约修正与无训练回归通过

### 启动边界与修改

- 按 `AGENTS.md` 完成新鲜启动核验：`ssh group-pc hostname` 为 `DESKTOP-KBM1345`；本机控制目录没有被当作代码仓库；远端 `git status` 中既有 dirty worktree 和未跟踪文件全部保留。本轮没有执行 `git add`、commit、push、pull、rebase 或分支切换。
- 完整读取了远端最新 `WORKLOG.md`、批准设计、原实施计划和 `2026-09-08-bdd100k-task10-remediation-and-continuation.md`；本机日志与远端日志不一致时以远端日志为准。
- 只执行用户授权的最小 Phase A 修正和无训练回归：没有创建或启动 Scheduled Task，没有重跑 `DDM4IP-BDD100K-SYNTH-Oracle-Pilot-v1`，没有下载/准备权重，没有 GPU 推理、训练、正式评估或 benchmark 数据处理。
- 修改 `ddm4ip/configs/dataset/bdd100k_synthetic_paired.yaml`：增加物理目录字段 `pairs_dir: test-paired`，将数据路径改为 `${paths.data}/${dataset.test.pairs_dir}/pairs.jsonl`，保留逻辑 `pairs_role`/`role` 契约。
- 修改 `scripts/bdd100k_synthetic_runner.py`：Oracle pilot 在固定 `dataset.test.pairs_role=dev_reserve` 的同时注入 `dataset.test.pairs_dir=dev-reserve`；`validate_spec` 固定 Oracle pilot 必须使用 `dev-reserve/pairs.jsonl` 和 16 条记录，继续通过原有 allowlist、benchmark preflight 和 hash 校验。
- 修改 `tests/test_bdd100k_synthetic_runner.py`，新增逻辑角色到冻结物理目录的 runner 合同测试，并覆盖错误 manifest 被拒绝；修改 `tests/test_bdd100k_synthetic_configs.py`，将 direct Hydra 回归期望更新为 `dev-reserve/pairs.jsonl`。

### TDD 与无训练验证证据

- 红灯 1：新增 `dataset.test.pairs_dir=dev-reserve` 断言后，runner 聚焦测试为 24 tests、1 failure、退出码 1，稳定复现修复前缺失 override。
- 红灯 2：新增 Oracle pilot 冻结 manifest 安全断言后，runner 聚焦测试为 24 tests、1 failure、退出码 1，证明不接受任意替代目录。
- 聚焦绿灯：runner/config 测试共 27 tests、退出码 0、`OK`。
- 完整回归：`E:\Anaconda3\envs\ddm4ip\python.exe -m unittest discover -s tests -v` 共 67 tests，`Ran 67 tests in 15.695s`，退出码 0，`OK`。TEMP/TMP、pip、Torch/XDG、MPL 和 PyCache 均指向 `D:\DDM4IP-runtime\temp\phaseA-path-fix-20260908` 等 D 盘项目临时目录。
- 四个真实 Hydra 配置解析均只使用 `--cfg job --resolve`，没有构造数据集或进入训练：`step1_bdd100k_synthetic`、`step2_bdd100k_synthetic`、`step3_bdd100k_oracle`、`step3_bdd100k_synthetic` 全部退出码 0，组合总退出码 0。
- Oracle dry-run 由 runner 生成 allowlisted command，并执行固定 Python 的 `ddm4ip.main ... --cfg job --resolve`；runner preflight 先核对 benchmark 文件。结果为 `stage=oracle`、`variant=oracle`、`mode=pilot`、`pairs_role=dev_reserve`，`pairs_dir=dev-reserve`，实际路径 `D:\DDM4IP-runtime\synthetic-benchmarks\bdd100k-motionblur-v1\dev-reserve\pairs.jsonl`，`max_imgs=16`，`expected_records=16`，`noise.std=0.02`，child dry-run 退出码 0，辅助脚本退出码 0。
- Oracle dry-run 三项 benchmark hash 完整匹配：summary=`97F874E8497F4F8FB2C814B814C15E3C43CC736AFC344DF449E58C99D58A346E`，`dev-reserve/pairs.jsonl`=`482277FD47D395B369A5C0E53E3BB7D7006133F8D819DE0501E878E6F8395530`，`degradation/kernel-gt.pt`=`4E292CA42C026965EF9B6D16CACEC83091DFC2E461C2C6788C6FDC690F832A7A`。

### 修改后 SHA-256 与独立收尾核验

- `scripts/bdd100k_synthetic_runner.py`：`9ED9344827D11A051AD60416A4E9F8085A9026D89105C15E48F76510CE4C8710`。
- `ddm4ip/configs/dataset/bdd100k_synthetic_paired.yaml`：`D33F1F953F83C12D640B789767C6C54F20F0F2C9276C925C448549CD297616A7`。
- `tests/test_bdd100k_synthetic_runner.py`：`F3A1082198BEAD692BD46D78F0559EB6CED089E24AD2132D6128DAF4C8863408`。
- `tests/test_bdd100k_synthetic_configs.py`：`4248B4422A0DFCC711C7E8952BDA35315882C8FAA90F70C36B5B31138854F648`。
- 独立远端验收再次确认 benchmark 三项 hash 未变；失败运行根仍存在且 `status.json` 为 `FAILED`、`exit_code=1`，历史仍为单次 `RESERVED -> RUNNING -> FAILED`。当前失败证据 hash 为 `task.log=0F97738C7EDC91BC64826FB2C0FB832659C548221435ADECB582A76AE14296F9`、`status.json=8189107AAD8361D9B52295DFFD9F89AA1B006F8C1859BB40F99598962A1BECAF`、`status-history.jsonl=094D8E4DCA5F680426C67114265AD9E94443363F4B9E1EBA5BC96ACA7278687E`。
- `DDM4IP-BDD100K-SYNTH-Oracle-Pilot-v1` 仍存在，当前 `State=Ready`、`LastTaskResult=1`；没有匹配的活动项目进程。失败运行根 `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot` 和失败任务均未覆盖、删除或重跑。
- 远端 `git status --short` 仅保留本次之前的 dirty worktree/未跟踪文件及上述四个修改文件；没有 Git 写操作。新增的 D 盘临时回归目录 `D:\DDM4IP-runtime\temp\phaseA-path-fix-20260908` 属于本项目独占的测试/dry-run 临时目录，不含 benchmark 或模型产物。

### 下一阶段准入

- Phase A 修正和无训练证据已通过；Phase C Oracle GPU pilot 仍未执行。必须在新的对话中由用户重新明确授权，并使用新的 task/run root；不得复用或改写本次 FAILED run root，也不得把本次 dry-run、配置解析或测试结果当作 GPU pilot 通过。

## 2026-09-08：Phase C Oracle GPU pilot 首次启动失败（dev-reserve 路径契约阻塞，未执行 GPU 推理）

### 启动前门禁

- 本轮重新完成 `AGENTS.md` 启动核验：本机主机名为 `zzz`，未把本机同名路径当作仓库；`ssh group-pc hostname` 为 `DESKTOP-KBM1345`。远端仓库为 `D:\Unsupervised Imaging Inverse Problems`、分支为 `main`，既有 dirty worktree 和未跟踪文件全部保留，未执行 Git 写操作。
- 完整读取了批准设计、原实施计划、本修正与后续总计划以及远端最新 `WORKLOG.md`。本机日志与远端日志不一致，本轮以远端为准。
- 启动前新鲜核对 benchmark 状态为 `SUCCESS`，角色计数 `1000/100/500/139`；summary SHA-256=`97F874E8497F4F8FB2C814B814C15E3C43CC736AFC344DF449E58C99D58A346E`，`dev-reserve/pairs.jsonl` SHA-256=`482277FD47D395B369A5C0E53E3BB7D7006133F8D819DE0501E878E6F8395530`，`degradation/kernel-gt.pt` SHA-256=`4E292CA42C026965EF9B6D16CACEC83091DFC2E461C2C6788C6FDC690F832A7A`；dev pairs 记录数为 139。
- 通过新鲜网络守卫离线构造门：Phase C preflight v3 的 `offline-result.json` 位于 `D:\DDM4IP-runtime\temp\phaseC-preflight-20260908-v3\offline-result.json`；实际构造 LPIPS AlexNet、DRUNet 和 DPIR 均成功，AlexNet/DRUNet 大小与 SHA 与 Phase B 一致，`network_guard_hits=0`，`HF_HUB_OFFLINE=1`、`TRANSFORMERS_OFFLINE=1`，`tempfile_gettempdir`、TEMP/TMP、Torch/XDG/PyCache/MPL 目录均在 D 盘。
- 启动前目标 Oracle run root 与同名任务均不存在。冻结外部 spec 位于 `D:\DDM4IP-runtime\experiments\phaseC-oracle-pilot-spec-20260908.json`，本机上传副本与远端 SHA-256 均为 `A33B16F319A4EAB1E0A1E1B0067CE9A33FB7090CA1DE48AE8AD267C55C98CEC2`；runner SHA-256=`A2F7E1B6AD5127E4289A1B26C5067DC048CCB6337491DFDD9B4E1587A5B6F7D5`。spec 冻结 `stage=oracle`、`mode=pilot`、`variant=oracle`、无 seed/predecessor、`max_imgs=16`、`expected_manifest_records=16` 及上述三项 benchmark 哈希。

### 任务结果与独立复核

- 通过 `start_bdd100k_synthetic_task.ps1` 唯一 launcher 创建并启动 `DDM4IP-BDD100K-SYNTH-Oracle-Pilot-v1`；run root 为 `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot`。任务记录一次运行：`LastRunTime=2026-09-08T15:22:01+08:00`、`LastTaskResult=1`、当前 `Ready`；run root 的 `status-history.jsonl` 按 JSON 对象边界为 `RESERVED -> RUNNING -> FAILED`，没有重复运行记录。
- `status.json` 为 `FAILED`、`exit_code=1`；`task.log` 保留完整 Hydra 解析和 traceback，失败发生在 `ManifestPairedDataset` 构造读取 pairs 前，目标 `plots` 未生成，复核时没有匹配的 runner/Oracle 进程。因此本次没有进入 GPU 推理、没有训练、没有正式 500 图评估，也没有改写 benchmark 或旧运行根。
- 失败日志的关键路径为：`D:\DDM4IP-runtime\synthetic-benchmarks\bdd100k-motionblur-v1\dev_reserve\pairs.jsonl` 不存在；实际冻结目录为 `dev-reserve\pairs.jsonl`。

### 根因与边界

- 当前 `ddm4ip/configs/dataset/bdd100k_synthetic_paired.yaml` 使用 `path: ${paths.data}/${dataset.test.pairs_role}/pairs.jsonl`；当前 runner 的 Oracle pilot override 固定注入 `dataset.test.pairs_role=dev_reserve`。因此 Hydra 解析出下划线路径 `dev_reserve`，而 benchmark 设计和 spec 的清单路径使用连字符目录 `dev-reserve`。runner 的 `pairs_manifest=dev-reserve/pairs.jsonl` 只用于 hash/preflight/evaluation 注入，没有修正数据集的 Hydra 路径。
- 这是 Phase A 无训练合同测试未覆盖的真实配置/目录命名契约缺口，不是 benchmark 缺失，也不是权重或 GPU/CUDA 问题。按阶段边界，本轮不直接修改代码、不创建第二个任务、不重跑或删除失败证据；Phase C 不能标记为通过，Task 11 仍不准入。
- 下一准入是单独授权的最小 Phase A 修正/回归：先为 `dev_reserve -> dev-reserve` 的实际数据路径补充红灯测试，修复 runner/config 路径合同并重新通过聚焦/完整无训练测试、Oracle dry-run 和四配置解析；之后用户需在新对话重新明确授权 Phase C 新版本 task/run root，不能复用本次 FAILED root。

### 本阶段清理清单增量

- `D:\DDM4IP-runtime\experiments\phaseC-oracle-pilot-spec-20260908.json`：冻结外部 Phase C spec。
- `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot`：本次失败 Oracle 运行根，包含 `status.json`、`status-history.jsonl`、`task.log`、Hydra 配置和失败证据；不得覆盖或删除。
- `D:\DDM4IP-runtime\temp\phaseC-preflight-20260908`、`D:\DDM4IP-runtime\temp\phaseC-preflight-20260908-v2`、`D:\DDM4IP-runtime\temp\phaseC-preflight-20260908-v3`：本项目专用离线门禁/诊断证据目录；未删除。

## 2026-09-08：修正总计划 Phase B 完成（LPIPS AlexNet 主干权重与离线总验收）

### 独立终验结论

- Phase B 已通过独立终验。唯一新建的计划任务 `DDM4IP-Task10-LPIPS-AlexNet-Weights-v1` 当前为 `Ready`，`LastTaskResult=0`，触发器数为 `0`；`status.json` 为 `SUCCESS`、步骤为 `offline_construct_complete`。`status-history.jsonl` 按完整 JSON 对象边界解析得到 5 条记录，状态序列为 `RUNNING`、`RUNNING`、`RUNNING`、`RUNNING`、`SUCCESS`；`task.log` 的最终记录为 `SUCCESS offline_construct exit_code=0`。
- AlexNet 主干目标 `D:\DDM4IP-runtime\torch-home\hub\checkpoints\alexnet-owt-7be5be79.pth` 已独立核对为 `244408911` bytes，SHA-256=`7be5be791159472b1fbf3c69796f7cb30dca7ad8466c2df70058c37116cdee02`。
- 既有 DRUNet 权重 `D:\DDM4IP-runtime\torch-home\hub\checkpoints\drunet_deepinv_color_finetune_22k.pth` 已独立核对为 `130585443` bytes，SHA-256=`20296845d272d3d786b89ea3c1208d5f2ceb57658a499d4dd28073cbb73508aa`。
- 独立验收脚本 `D:\DDM4IP-runtime\weights\task10-lpips-alexnet-offline-independent-20260908-v1\independent-audit.py`（SHA-256=`8D7D7CC779F6714B5C02A93F5FDBD9ACC5884269FAB20D47CCEA7962C0662205`）退出码为 `0`；实际独立构造日志为 `D:\DDM4IP-runtime\weights\task10-lpips-alexnet-offline-independent-20260908-v1\independent-offline-construction.log`，结果文件为同目录 `independent-offline-result.json`。
- 在进程级 `HF_HUB_OFFLINE=1`、`TRANSFORMERS_OFFLINE=1`、D 盘 `TEMP/TMP/TORCH_HOME/XDG_CACHE_HOME/PIP_CACHE_DIR` 下，独立进程实际构造了 LPIPS（`alexnet`）、DRUNet 和 DPIR；三者均为 CPU，网络拦截命中 `0`。任务自身结果与独立结果均一致。

### 授权边界与保留证据

- 首次 v1 运行根 `D:\DDM4IP-runtime\weights\task10-lpips-alexnet-download-20260908-v1` 的缺少脚本失败证据、v1b 成功运行根及其状态/日志均保留；未清理、覆盖或改写旧失败证据。v1b 运行根为 `D:\DDM4IP-runtime\weights\task10-lpips-alexnet-download-20260908-v1b`。
- 本阶段未启动 Oracle、GPU 推理、训练、正式评估或真实数据处理；未创建第二个计划任务。Phase B 成功不等于 Phase C 或 Task 11 获得授权。
- 下一步准入：如需继续，用户必须在新对话中明确授权修正总计划 Phase C（16 图 Oracle GPU pilot）；在该授权出现前不得启动 Oracle，也不得进入 Task 11。上述 D 盘权重、缓存、日志和独立验收目录属于本项目清理清单，当前不执行清理。

## 2026-09-08：修正总计划 Phase B 进行中（LPIPS AlexNet 权重准备）

### 本轮授权与已完成核验

- 本轮仅执行用户明确授权的修正总计划 Phase B：准备 LPIPS AlexNet 主干权重并在终态后完成离线总验收；未授权、未执行 Oracle、GPU 推理、训练、正式评估、真实数据处理或清理旧失败证据。Phase B 成功不自动授权 Phase C 或 Task 11。
- 已重新完成启动核验：`ssh group-pc hostname` 为 `DESKTOP-KBM1345`；远端仓库为 `D:\Unsupervised Imaging Inverse Problems`，分支为 `main`。远端 dirty worktree、既有修改和旧失败运行根均保留；本轮未执行 Git 写操作。
- 本轮核验的远端盘空间为 C=`21,264,072,704` bytes、D=`109,797,474,304` bytes、E=`44,503,461,888` bytes。计划任务进程级 `TEMP/TMP/TORCH_HOME/XDG_CACHE_HOME/PIP_CACHE_DIR` 均指向 `D:\DDM4IP-runtime` 下的项目专用目录；未修改系统级或用户级环境变量。
- 目标文件 `D:\DDM4IP-runtime\torch-home\hub\checkpoints\alexnet-owt-7be5be79.pth` 在启动前不存在。固定官方来源为 `https://download.pytorch.org/models/alexnet-owt-7be5be79.pth`；DRUNet 既有独立离线通过记录仍为 130,585,443 bytes、SHA-256=`20296845d272d3d786b89ea3c1208d5f2ceb57658a499d4dd28073cbb73508aa`。

### 计划任务与运行证据

- 新建且唯一登记的计划任务为 `DDM4IP-Task10-LPIPS-AlexNet-Weights-v1`，触发器数为 `0`，仅手动启动。首次运行根 `D:\DDM4IP-runtime\weights\task10-lpips-alexnet-download-20260908-v1` 因缺少 `download-alexnet.py` 立即失败；`status.json`、`status-history.jsonl`、`task.log`、计划任务结果和运行根均保留，目标权重未被该失败运行写出。
- 为保持“只允许一个新的、唯一的权重准备计划任务”的授权边界，未注册第二个任务；仅将同一任务对象的动作改指向新的独立运行根 `D:\DDM4IP-runtime\weights\task10-lpips-alexnet-download-20260908-v1b`，并补齐三个脚本。脚本 SHA-256 分别为：`run-weight-task.ps1`=`511E1E4B8E696504A00722B7B7E77775836B9E69C22CB7A16AC10C9DBB6CABD7`、`download-alexnet.py`=`7563C437EE9A5F30484AE1C30EA050A1FBE1A7199C1083D3E43176EE45CF5809`、`offline-construct.py`=`5934618CAA4DD1B818BD934463046D05258C2BCDCCE6114B9E621457CDA91E56`；PowerShell 解析和 Python 编译检查均退出码 `0`。
- 最近一次独立检查时，v1b 状态为 `RUNNING`、当前步骤为 `download`，更新时间为 `2026-09-08T13:06:03.2306256+08:00`；计划任务 `LastTaskResult=267009 (0x41301)`，表示仍在运行，不是失败；动作路径、状态文件和任务日志均已落在 D 盘。此时目标 AlexNet 文件和 `offline-result.json` 尚未出现，因此 Phase B 尚未完成，不能写成成功。

### 已知问题与下一步准入

- 首次独立终检发现现有 `status-history.jsonl` 记录由 PowerShell `ConvertTo-Json` 产生多行 JSON，不能用“逐行 `ConvertFrom-Json`”解析；这只是验收读取命令的问题，没有改写任务历史、状态或日志。终态验收必须使用能按 JSON 对象边界解析的读取方式，并同时核对 `status-history.jsonl`、`task.log`、`status.json`、`LastTaskResult`、目标文件字节数与 SHA-256。
- 待 v1b 自然进入终态后，用户可先在远端查看状态；用户确认终态后，本项目助手须重新连接并独立核对下载结果，在 `HF_HUB_OFFLINE=1`、`TRANSFORMERS_OFFLINE=1` 下实际构造 LPIPS AlexNet、DRUNet 和 DPIR，全部通过后才可记录 Phase B 成功。即使 Phase B 成功，仍需用户在新对话中明确授权 Phase C Oracle GPU pilot；不得据此启动 Task 11。

## 2026-09-08：完成 Task 10 修正总计划 Phase A（仅代码与无训练回归）

### 授权、启动核验与边界

- 本轮只执行用户明确授权的修正总计划 Phase A：修复 Task 10 前置代码、synthetic runner、wrapper、最终聚合器和无训练回归测试；未下载任何权重，未创建或启动 Scheduled Task，未运行 Oracle/GPU 推理、训练、正式评估或真实数据处理，未修改 benchmark、历史运行根或既有真实 BDD100K 主线。
- 按 `AGENTS.md` 完成启动核验：`ssh group-pc hostname` 为 `DESKTOP-KBM1345`；远端仓库为 `D:\Unsupervised Imaging Inverse Problems`，分支为 `main`。远端原有 dirty worktree 和用户修改均保留；本轮未执行 `git add/commit/push/pull/rebase` 或切换分支。
- 启动时已读取本机 WORKLOG、远端 WORKLOG、批准设计、原实施计划和 `docs\superpowers\plans\2026-09-08-bdd100k-task10-remediation-and-continuation.md`。远端 benchmark 已存在，DRUNet/DPIR 离线门已有独立通过记录；Task 10 Oracle 尚未运行，Task 11 尚未准入。

### TDD 红灯/绿灯证据

- A1：新增 Oracle variant、命令映射、16 图 dev-reserve/hash/std 合同测试；红灯 `16` tests，`1 failure + 2 errors`，退出码 `1`；最小实现后绿灯 `16/16`。
- A2：新增 16 图 writer 生命周期、统一 manifest/metrics/summary schema、必需 prediction/kernel/provenance SHA、PNG 保存后指标复算和 aggregator 合同测试；红灯阶段记录为 `8` tests、`6 errors`、退出码 `1`（初始测试 fixture 的非法占位 hash/尺寸问题已修正并重新运行）；实现后绿灯 `8/8`。
- A3：新增 preflight/postflight、run-root/Hydra 绑定、真实 `subprocess.run` fixture child、stdout/stderr 合并日志和故意损坏工件测试；红灯 `16` tests、`3 failures`、退出码 `1`；实现后绿灯 `16/16`。
- A4：新增 predecessor/checkpoint stage、seed、SHA、global step、model key 和 pickle 临时 `sys.path` 测试；红灯 `20` tests、`5 errors`、退出码 `1`；实现后绿灯 `20/20`。
- A5：新增 wrapper 静态单次触发、离线缓存和 PowerShell parser 测试；红灯 `22` tests、`1 failure`、退出码 `1`；实现后绿灯 `22/22`。
- A6：新增 CLI 五个 kernel result 必需输入及跨 seed mean/std、kernel PSNR/NCC 测试；红灯 `6` tests、`1 error`、退出码 `1`；实现后绿灯 `6/6`。
- 追加 schema 严格字段测试：红灯 `1 error`、退出码 `1`；实现后 `1/1`。追加 Step 3 配置字段测试：红灯 `1 error`、退出码 `1`；实现后 `1/1`。追加 learned Step 3 `evaluation.step2_seed` 测试：红灯 `1 failure`、退出码 `1`；实现后 `1/1`。
- 最终新鲜回归：聚焦四模块 `35/35`，运行时间 `9.030s`，退出码 `0`；完整远端 `unittest discover -s tests -v` 为 `66/66`，运行时间 `14.222s`，退出码 `0`。

### 已实现并验证的合同

- `BenchmarkMetricWriter` 在第 1—15 张图只追加 `manifest.jsonl`/`metrics.jsonl`，第 16 张且恰好达到 expected count 才 finalize `summary.json`；重复 source、超额记录、非有限指标、seed/hash 不一致 fail closed。
- trainer 保存 prediction PNG 后重新读取 PNG 计算正式 restored 指标，写入 prediction/kernel 文件 SHA 和完整 provenance；runner 固定从 `<run_root>\plots` 做 preflight/postflight，summary、JSONL、source set、数值和方向均复核。
- Oracle pilot override 固定为 `stage=oracle`、`variant=oracle`、`pairs_role=dev_reserve`、`max_imgs=16`、`expected_records=16`、`noise.std=0.02`，并注入完整 benchmark/pairs/kernel hash；learned Step 3 注入同 seed 的 `evaluation.step2_seed`。
- 无训练真实 execute 使用 `tests\fixtures\synthetic_execute_child.py`，实际经过 `subprocess.run`；成功 fixture 得到 SUCCESS，损坏 fixture 得到 FAILED，stdout/stderr 均追加到根 `task.log`。没有用 mock returncode 代替该验证。
- predecessor 解析冻结为 stage/run_root/expected_step/两份 checkpoint 路径与 SHA/seed；`.pt` 为 N、`.pkl` 为 N+1，分别校验 `flow_nn`/`kernel_nn`；pickle 期间临时注入项目根 `sys.path` 后恢复原值。
- start wrapper 静态验证无 `New-ScheduledTaskTrigger`、仅一个字面量 `Start-ScheduledTask`，execute 使用 reserved `<run_root>\spec.json`；stage wrapper 使用 `D:\DDM4IP-runtime\torch-home` 及两个 offline flag。runtime schema 已严格冻结 predecessor 和三项 benchmark hash。
- aggregator 强制 `1 Oracle + 5 learned seed + 5 kernel analysis`，逐运行重新读取 JSONL/manifest 并复核 SHA、source set 和统计，输出跨 seed mean/std 及 kernel PSNR/NCC。

### 最终配置、parser、任务和 benchmark 证据

- 四个 Hydra 入口解析均退出码 `0`：`step1_bdd100k_synthetic`、`step2_bdd100k_synthetic`、`step3_bdd100k_oracle`、`step3_bdd100k_synthetic`。两个 wrapper 的 PowerShell `parse_errors=0`，parser 总退出码 `0`。
- 只读任务/进程核验未发现 Oracle/Step1/Step2/Step3 新任务或匹配进程。现存仅为此前的 `DDM4IP-BDD100K-SYNTH-Build-Provenance-Audit-v1`、`Build-v1`、`Inventory-v1`、`Inventory-v2`，均为既有任务；本轮未注册或启动任务。
- benchmark 未改写；当前 SHA-256 仍为：summary `97F874E8497F4F8FB2C814B814C15E3C43CC736AFC344DF449E58C99D58A346E`；test pairs `3C86E1B8CC419E6FDB627EB60D7C6DD209015123EEC44F790D0115B39BFFF9E4`；dev-reserve pairs `482277FD47D395B369A5C0E53E3BB7D7006133F8D819DE0501E878E6F8395530`；kernel `4E292CA42C026965EF9B6D16CACEC83091DFC2E461C2C6788C6FDC690F832A7A`。

### Phase A 关键文件 SHA-256

```text
A2F7E1B6AD5127E4289A1B26C5067DC048CCB6337491DFDD9B4E1587A5B6F7D5  scripts\bdd100k_synthetic_runner.py
524AC69BE5BD4A74B905650124C85397503A0C554BA378A7310DFD0F73B6B8CA  scripts\aggregate_bdd100k_synthetic_results.py
939CA21B2E0DCC44EAF4B88D1B51F1DABA11ACBB27A1A12085F5782C725EBCDE  ddm4ip\utils\benchmark_metrics.py
13ECD951E9C521B2AFAC42FE2EC1ABCD4452B4BE3FA9B0F57DFCE68795B99B69  ddm4ip\trainers\deepinv_denoiser.py
8E780E42B7A0024B41EA36FF58E6C5C24708A09BB48341BD5BE7C06EAAD23A8F  ddm4ip\configs\dataset\bdd100k_synthetic_paired.yaml
F25A0283AE702B1812B6FAEB47BFBFDC105D0A802C8F8A8924B42CC07BF5A0A6  ddm4ip\configs\exp\step3_bdd100k_oracle.yaml
24710EED47C3B20658DAA0E47451A9707E50DDDC61E40A2B3A8E4F98BB221920  ddm4ip\configs\exp\step3_bdd100k_synthetic.yaml
18C11F51C52C34D05D3C147BC42C2136A5E096D4CECC0A992D50CB2C8D79CF5B  tests\test_bdd100k_synthetic_runner.py
46DA48908F2FC27BD4AD18B9575E87C6A1C74E8A18537FD3523E4DC0B078DF08  tests\test_benchmark_metrics.py
DF56B3AD3826A6D68E6F4EACD1EDFC40A81DB1DE235E34A7FD72C491F8BA5868  tests\test_bdd100k_synthetic_trainer.py
5B2300B2DC6248E46C186FF103920FE620FF4C0011D4055CE247B256F0AA9FE4  tests\test_bdd100k_synthetic_configs.py
044EC3BB814FBE354C5FCA5F065671F8F9FD579355A1E72F217E7EA4B55D5EE3  tests\fixtures\synthetic_execute_child.py
DDA9FAA08DCC6C0396D1AC9852DB197E2FA09DEB4E037DE24AC81925645D560A  D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1
6E9DC30A6176001DC58ED3E94EB7957DAD63B66FB61969EA464198CCB6FF42CB  D:\DDM4IP-runtime\orchestration\run_bdd100k_synthetic_stage.ps1
4712125719DBE2BFE255D420C7C275BBF93A6C7DAF7C627A073C0E096E8682C8  D:\DDM4IP-runtime\orchestration\synthetic-step-spec.schema.json
```

### 已知风险、清理清单与下一门禁

- AlexNet LPIPS 主干 `alexnet-owt-7be5be79.pth` 仍未在规范 D 盘缓存中独立验收；Phase A 不下载、不重试。Task 10 Oracle 未运行，Step 1/2 learned checkpoint 不存在，Task 11 未准入。下一门必须是新对话、用户单独授权的 Phase B。
- Phase A 仅用 fixture child 做真实 execute；没有真实 GPU、Oracle 或正式数据评估。wrapper 的实际任务注册/启动未调用，这是本轮“不得创建或启动计划任务”边界内的静态契约验收。
- Phase A 项目专用测试证据目录均未删除，清理时只允许按精确路径处理：
  `D:\DDM4IP-runtime\phaseA-a2-green`、`phaseA-a3-green1`、`phaseA-a3-green2`、`phaseA-a3-red`、`phaseA-a4-green`、`phaseA-a4-green2`、`phaseA-a4-red`、`phaseA-a5-green`、`phaseA-a5-red`、`phaseA-a6-green`、`phaseA-a6-red`、`phaseA-a7-focused`、`phaseA-a7-full`、`phaseA-a7-schema-green`、`phaseA-a7-schema-red`、`phaseA-config-field-green`、`phaseA-config-field-red`、`phaseA-final2-focused`、`phaseA-final-config`、`phaseA-final-config2`、`phaseA-final-config3`、`phaseA-final-focused`、`phaseA-final-full`、`phaseA-seed-green`、`phaseA-seed-red`。这些是本项目独占的 Phase A 测试/证据目录，未删除。
- Phase A 完成不等于 Task 10 完成，也不授权 Phase C、Task 11 或任何训练。Phase B 的准入条件是：新鲜核验 C/D/E 空间和进程级缓存路径；通过一个新的、唯一的权重准备任务获取 AlexNet；记录目标文件字节数/SHA；在 offline guard 下实际构造 LPIPS AlexNet、DRUNet 和 DPIR，且所有缓存/日志/临时文件在 D 盘；旧失败证据不得覆盖。

### 下一对话建议

```text
请先按 AGENTS.md 完成完整启动核验，并完整阅读已批准设计、原实施计划、2026-09-08-BDD100K-Task10-修正与后续执行总计划.md、远端最新 WORKLOG.md。
当前已完成 Phase A：代码与无训练回归；benchmark 已存在；DRUNet/DPIR 离线门已有独立通过记录；Oracle 尚未运行；Task 11 尚未准入。
本对话只授权执行修正总计划 Phase B：仅准备 LPIPS AlexNet 主干权重并完成离线总验收。允许创建并启动一个新的、唯一的权重准备计划任务；不授权 Oracle、GPU 推理、训练、正式评估、真实数据处理或清理旧失败证据。
权重、临时文件、日志和缓存只能落在 D:\DDM4IP-runtime；先核验 C/D/E 空间、进程级 TEMP/TMP/TORCH_HOME/XDG_CACHE_HOME，并保留失败运行根。完成后独立核对任务状态历史、日志、LastTaskResult、目标文件字节数和 SHA-256，并在 HF_HUB_OFFLINE=1、TRANSFORMERS_OFFLINE=1 下实际构造 LPIPS AlexNet、DRUNet 和 DPIR；不要把 Phase B 成功当作 Phase C 授权。
```

## 2026-09-08：生成 Task 10 修正与后续执行总计划（未改代码、未启动运行）

- 本轮按 `AGENTS.md` 重新核验：完整读取本机与远端 `WORKLOG.md`，`ssh group-pc` 主机名为 `DESKTOP-KBM1345`，远端仓库为 `D:\Unsupervised Imaging Inverse Problems`、分支为 `main`；全部既有修改和未跟踪文件均保留。远端日志比本机日志更新，本轮继续以远端为准。
- 已再次完整读取批准设计和 820 行原实施计划，并基于 2026-09-08 的只读代码审查编写补充计划 `docs\superpowers\plans\2026-09-08-bdd100k-task10-remediation-and-continuation.md`；SHA-256=`2AEF832E0EA5CD47473E6A118062A0371C3748333CFD4446E5ED5D11FBEA6FF3`。
- 新计划把修复链拆为：Phase A 代码/runner/wrapper/聚合器与无训练测试；Phase B AlexNet 权重准备和 LPIPS+DRUNet+DPIR 离线总验收；Phase C Task 10 的 16 图 Oracle GPU pilot；通过后才依次进入 Task 11 pilots、Step 1 full，以及 Tasks 12–14。文档含 14 个已确认问题、测试先行步骤、真实无训练 execute、16 图 writer、统一 schema/哈希、run-root、predecessor/checkpoint、单次触发、PNG 指标复算和跨 seed 聚合门。
- 本文和复选框不构成阶段授权。当前下一项仍是由用户在新对话中单独授权 Phase A；本轮没有修改项目代码/runtime wrapper，没有下载 AlexNet 权重，没有创建或启动计划任务，没有运行 Oracle、训练、评估或数据处理。

## 2026-09-08：Task 10 与后续执行链只读审查发现阻塞（未启动任何运行）

### 启动核验与新鲜状态

- 已按 `AGENTS.md` 完成完整启动核验：完整读取本机控制日志；`ssh group-pc` 确认为 `DESKTOP-KBM1345`；远端仓库为 `D:\Unsupervised Imaging Inverse Problems`、分支为 `main`，全部既有修改与未跟踪文件均保留；远端 `WORKLOG.md` 比本机版本更新且两者不一致，本轮以远端为准，未覆盖本机日志。
- 已完整读取批准设计和 820 行实施计划；SHA-256 仍分别为 `6238E075F8FB37F5823FD0EF362553F8C873970B63DA428BD6B66B218A42E555` 与 `1B8F44A1B95B6B7CAA58DB22981F6DC25DA390A0912AB0339B6870E70A492C97`。
- benchmark、500 行 test pairs、139 行 dev pairs、32×32 真核和 DRUNet 文件仍存在且哈希与既有验收一致；Oracle pilot 运行根不存在，没有 Oracle 计划任务或相关进程。因此 Task 10 尚未执行，不是已运行后失败；Task 11 仍不准入。
- 新鲜运行完整无训练回归为 `53/53`、退出码 `0`；四个 synthetic Hydra 模块入口解析均退出码 `0`。这些测试未覆盖下述真实 execute 链缺口，不能据此声明 Task 10 可运行。

### 已确认的 Task 10/后续阻塞

- `scripts\bdd100k_synthetic_runner.py` 的 Oracle 契约不一致：计划文字要求 `stage=oracle, variant=oracle`，当前校验却只允许 `step3` 携带 variant。Oracle pilot 只注入 `dataset.test.pairs_role=dev_reserve`，而 `evaluation.expected_records`、`kernel_gt_path/hash`、`pairs_manifest_sha256` 仅对 `stage=step3` 注入。精确 dry-run 因而解析为 `dev_reserve/max_imgs=16`，但仍是 `expected_records=500`、`kernel_gt_path=null`、`pairs_manifest_sha256=null`。
- `ddm4ip\configs\dataset\bdd100k_synthetic_paired.yaml` 没有把 Gaussian `std` 固定为 `0.02`；当前 Oracle 解析值为 `0.04`，与冻结 benchmark 和批准设计不符，会给 DPIR 错误噪声水平。
- `BenchmarkMetricWriter.write_summary()` 要求当前行数立刻等于 expected count，但 trainer 每处理一张图就调用；16 图 pilot 会在第 1 图后以 `expected 16, found 1` 失败并留下部分工件。现有 trainer 测试只使用 `expected_count=1`，因此未发现。
- trainer 将定量工件写入 `<run_root>\plots`，runner 的验收函数却从 `<run_root>` 读取；trainer manifest 没有 runner 要求的 `prediction_sha256`，writer summary 使用 `count/metrics`，runner 要求 `records/mean`，且 writer 只聚合 restored 指标、没有 input 汇总，无法执行 Oracle 改善方向验收。
- runner execute 未在子进程前核对 benchmark summary/pairs/kernel 的实际 SHA-256，未在子进程成功后调用 evaluation/checkpoint 验收；仅以原生退出码写 SUCCESS。`verify_checkpoint_pair()`/`verify_evaluation_artifacts()` 当前只有定义和直接单测，没有进入执行路径。
- Step 2 与 learned Step 3 execute 没有从 predecessor 解析、核验并注入 flow `.pt` 或 kernel `.pkl`；`main()` 调用 `stage_command(spec)` 时未传 checkpoint。Step 1 checkpoint 验收还错误地把 snapshot 模型键映射为 `kernel_nn`，与实际 Step 1 的 `flow_nn` 不符。
- runner 未把 reserved `run_root` 绑定到 `training.log_dir/exp_name`；当前 Hydra 输出固定落在 `${paths.out_path}/${exp_name}`。此外 trainer 工件位于 `plots`，与 runner 根目录分离。子进程 stdout/stderr 也未追加到 `task.log`，真实异常可能不在规定日志中。
- launcher 同时使用一分钟后触发器和立即 `Start-ScheduledTask`，会重复启动。现有 provenance audit 的运行根保持 `SUCCESS/exit_code=0`，但计划任务当前 `LastTaskResult=1`，且第二次因 `execution.claim` 在进入 runner 状态记录前失败；这证明现行编排会制造伪失败元数据。
- LPIPS AlexNet 主干的 `alexnet-owt-7be5be79.pth` 不在 `D:\DDM4IP-runtime\torch-home` 或 `torch-cache`。LPIPS 包只自带小型线性层权重；当前真实构造仍可能下载 ImageNet AlexNet，违反 Oracle 离线门。DRUNet 则在两个缓存根各有一份相同 SHA 的文件，当前可见但路径规范应统一为 `torch-home`。
- `aggregate_summaries()` 目前不复核 `metrics.jsonl`，不计算五 seed 数据集均值的跨 seed mean/std，也不接收五个 kernel PSNR/NCC 结果；Task 14 的正式汇总尚不能按计划完成。当前指标在保存 PNG 前按浮点预测计算，Task 14 从 8-bit PNG 独立复算时还需明确量化一致性或容差。

### 修复顺序与阶段边界

- 下一阶段应是一个新的、只授权“Task 10 前置代码/运行器修复与无训练回归”的对话：先补多图 writer、Oracle dry-run、真实 execute、output-root、schema/哈希、predecessor/checkpoint 和单次计划任务回归测试，再做最小修复；保持真实 BDD100K 主线不变。
- 代码修复通过后，另行授权 AlexNet 权重准备：只落到规范的 `D:\DDM4IP-runtime\torch-home\hub\checkpoints`，记录大小/SHA，并在网络调用守卫下实际离线构造 LPIPS + DRUNet + DPIR。不得把首次下载混入 Oracle pilot。
- 只有新的端到端无训练 runner 夹具、完整 `unittest`、四配置解析、真实 dev manifest/hash 预检、单次触发与日志/状态契约全部通过，才能在再一个新对话中单独授权 Task 10 Oracle GPU pilot。Task 10 的 16 图指标和工件独立验收通过后，才可另行授权 Task 11 Step 1 pilot；本轮不授权任何运行或训练。

### 本轮清理清单增量

- 完整测试保留的新夹具根包括 `D:\DDM4IP-runtime\temp\base-final-checkpoint-2w4akwo_` 与 `D:\DDM4IP-runtime\temp\step3-geometry-79y88yvs`；本轮进程级 matplotlib/pycache 目录为 `D:\DDM4IP-runtime\temp\review-mpl-20260908` 与 `D:\DDM4IP-runtime\temp\review-pycache-20260908`。均为本项目专用，未删除；目录清理仍由用户按精确路径手动执行。

## 2026-09-07：Task 11 阶段边界确认，尚未授权

- 本轮只读复核远端最新 WORKLOG 与已批准实施计划：当前通过的是 Task 10 DRUNet/DPIR 离线权重门，下一准入仍为 Task 10 Oracle GPU pilot；未创建或启动 Oracle 任务，远端没有匹配 `Oracle` 的计划任务。
- Task 11 不能仅凭权重门通过而启动。计划明确要求先完成并独立验收 Task 10 Oracle 的 16 张开发集结果；Oracle 通过后，还需在新的对话中单独授权 Task 11 的 Step 1 pilot。
- Task 11 pilot 必须按 `b01`、`b02`、`b04`、`b08`、`b16`、`b32` 顺序分别运行并逐次独立核验；只有 batch 32 在约定显存门槛下通过且损失、checkpoint 有限，才可在另一个新对话中单独授权 Step 1 full training。本次没有启动 Oracle、Task 11 pilot/full 或其他后续 Task。

## 2026-09-07：Task 10 DRUNet 权重 v3d 独立离线验收通过

- v3c 运行根和日志均保留。v3c 在 21:59:10 曾完成一次离线构造并记录 `SUCCESS`，但随后因计划任务重复触发，22:00:05 的防重跑保护将其最终状态写为 `FAILED`；这两条历史日志均未覆盖或删除。
- 新建独立运行根 `D:\DDM4IP-runtime\weights\task10-drunet-download-20260907-v3d` 和计划任务 `DDM4IP-Task10-DRUNet-Weights-v3d`，未覆盖 v2/v3/v3b/v3c。任务最终为 `Ready`、`LastTaskResult=0`；`status.json` 为 `SUCCESS`、`step=offline_construct_complete`、`offline_exit_code=0`。
- 目标文件 `D:\DDM4IP-runtime\torch-home\hub\checkpoints\drunet_deepinv_color_finetune_22k.pth` 独立核验为 `130585443` 字节，SHA-256=`20296845d272d3d786b89ea3c1208d5f2ceb57658a499d4dd28073cbb73508aa`；目标目录残留临时文件列表为空。v3d 日志为 `D:\DDM4IP-runtime\weights\task10-drunet-download-20260907-v3d\task.log` 和 `offline-construction.log`。
- v3d 进程级环境记录为 `HF_HUB_OFFLINE=1`、`TRANSFORMERS_OFFLINE=1`、`TORCH_HOME=D:\DDM4IP-runtime\torch-home`、`XDG_CACHE_HOME=D:\DDM4IP-runtime\xdg-cache`，`TEMP/TMP` 均位于 v3d 的 `temp` 子目录；未修改系统级或用户级环境变量。
- 在上述离线标志下实际构造成功：`drunet_type=DRUNet`、`dpir_type=DPIR`，且 `torch.hub.download_url_to_file` 被守卫为网络下载即失败；输出 `target_size=130585443`，因此本次通过的是实际离线 DRUNet/DPIR 构造门，不是仅检查文件存在。
- 本阶段没有启动 Oracle GPU pilot、Step 1/2 训练、Step 3 评估或其他后续 Task。下一阶段准入条件仍是用户在新对话中单独明确授权 Task 10 Oracle GPU pilot；权重准备成功不构成后续阶段授权。

## 2026-09-07：Task 10 DRUNet 权重门通过，Oracle 仍待新对话授权

### 启动核验与范围

- 本轮先完整读取本机 D:\Unsupervised Imaging Inverse Problems\WORKLOG.md，通过 ssh group-pc 核验主机名为 DESKTOP-KBM1345，远端仓库为 D:\Unsupervised Imaging Inverse Problems；远端分支为 main。远端 Git 状态中的全部既有修改和未跟踪文件均保留，未执行 add、commit、push、pull、rebase 或分支切换。
- 本轮完整读取批准的设计文档和实施计划；设计 SHA-256=6238E075F8FB37F5823FD0EF362553F8C873970B63DA428BD6B66B218A42E555，计划 SHA-256=1B8F44A1B95B6B7CAA58DB22981F6DC25DA390A0912AB0339B6870E70A492C97。本阶段授权仅覆盖 Task 10 DRUNet 权重准备，不覆盖 Oracle、Step 1/2 训练、Step 3 评估或其他后续 Task。

### 存储、缓存与网络诊断

- 诊断时远端剩余空间：C 盘 20,865,650,688 字节，D 盘 111,315,050,496 字节，E 盘 44,503,461,888 字节。项目临时、Torch、XDG、pip 和任务目录均继续使用 D:\DDM4IP-runtime 下的进程级路径，没有修改系统级或用户级环境变量。
- v2 失败运行根 D:\DDM4IP-runtime\weights\task10-drunet-download-20260907-v2、任务 DDM4IP-Task10-DRUNet-Weights-v2 和日志均保留；任务为 Ready、LastTaskResult=1、status=FAILED，原始错误为 HTTPS/TLS HttpRequestException/SocketException，远端主机关闭连接。
- 根因调查显示远端并非整体断网：pypi.org、files.pythonhosted.org 和 download.pytorch.org 的 HTTPS 预检可达；官方 Hugging Face 直连、显式公开 IP 和 Clash HTTP 代理路径均在连接/TLS 阶段 reset。默认 huggingface.co DNS 被 Clash TUN 解析到 198.18.1.42，公共 DNS 1.1.1.1/8.8.8.8 分别返回 173.244.217.42/173.252.108.3；WinHTTP 为直接访问。Clash 进程为 clash-windows-amd64，混合端口 127.0.0.1:17890，当前 GLOBAL 仅有 DIRECT/REJECT，没有可用代理节点。因此没有把任务结束、Ready 状态或下载曾启动误判为成功。

### 既有 v3 证据与新的独立验证

- 新鲜检查发现 D:\DDM4IP-runtime\weights\task10-drunet-download-20260907-v3 和任务 DDM4IP-Task10-DRUNet-Weights-v3 已在本轮之前存在，状态为 FAILED、任务 Ready、LastTaskResult=1；本轮未覆盖或删除。其 .pth.partial 文件独立核验为大小 130,585,443 字节、SHA-256=20296845d272d3d786b89ea3c1208d5f2ceb57658a499d4dd28073cbb73508aa，与 Hugging Face deepinv/drunet 提交 7e079a6 的精确文件大小/SHA-256 一致；该 partial 仍作为失败运行证据保留。
- 新建并启动计划任务 DDM4IP-Task10-DRUNet-Weights-v3b，运行根为 D:\DDM4IP-runtime\weights\task10-drunet-download-20260907-v3b。v3b 独立核验 v3 partial，复制到 staging 后再次得到大小 130,585,443 和 SHA-256=20296845d272d3d786b89ea3c1208d5f2ceb57658a499d4dd28073cbb73508aa，再以不覆盖方式落到目标路径 D:\DDM4IP-runtime\torch-home\hub\checkpoints\drunet_deepinv_color_finetune_22k.pth。v3b 的文件晋级成功，但离线构造步骤因 Windows PowerShell 5.1 传递 python -c 时丢失字符串引号而以 offline_exit_code=1 失败；v3b status.json、日志和脚本均保留，没有改写为成功。
- 新建并启动计划任务 DDM4IP-Task10-DRUNet-Weights-v3c，运行根为 D:\DDM4IP-runtime\weights\task10-drunet-download-20260907-v3c，只使用独立 .py 文件避免上述引号传递问题。任务最终为 Ready、LastTaskResult=0，status=SUCCESS、step=offline_construct_complete、offline_exit_code=0。在 HF_HUB_OFFLINE=1、TRANSFORMERS_OFFLINE=1、TORCH_HOME=D:\DDM4IP-runtime\torch-home、XDG_CACHE_HOME=D:\DDM4IP-runtime\xdg-cache 下，实际构造 DRUNet(pretrained="download", device="cpu") 和 deepinv.optim.DPIR(sigma=0.1, denoiser=denoiser, device="cpu") 均通过；torch.hub.download_url_to_file 被守卫为网络调用即失败，离线日志输出 drunet_type=DRUNet、dpir_type=DPIR。

### 最终权重验收

- 目标文件存在于 D:\DDM4IP-runtime\torch-home\hub\checkpoints\drunet_deepinv_color_finetune_22k.pth，大小 130,585,443 字节，SHA-256=20296845d272d3d786b89ea3c1208d5f2ceb57658a499d4dd28073cbb73508aa；目标目录没有残留 .partial、.staging 或 .tmp 文件被当作权重。
- v3c 状态、日志和离线构造输出路径均在 D:\DDM4IP-runtime\weights\task10-drunet-download-20260907-v3c；v2、既有 v3 和 v3b 失败运行根均保留作为诊断证据。没有安装本机项目依赖，没有运行项目代码、训练、Oracle GPU 推理或评估。

### 下一阶段准入

- DRUNet/DPIR 离线权重门现已通过，但这不等于 Oracle 已启动。必须等待用户在新的对话中单独明确授权 Task 10 Oracle GPU pilot；本轮不授权、不创建、不启动 Oracle 计划任务，也不授权 Step 1/2 训练或 Step 3 评估。

## 2026-09-07：Task 10 DRUNet 权重准备仍失败，Oracle 门禁未解除

### 新鲜核验结果

- 本轮按 `AGENTS.md` 完成启动核验：`ssh group-pc` 主机名为 `DESKTOP-KBM1345`，仓库为 `D:\Unsupervised Imaging Inverse Problems`；远端分支为 `main`。远端工作区已有用户修改和未跟踪文件均保留，本轮未执行 Git 写操作、提交、拉取、推送、变基或分支切换。
- 已完整读取批准的设计 `docs\superpowers\specs\2026-09-06-bdd100k-known-blur-quantitative-reproduction-design.md`（SHA-256=`6238E075F8FB37F5823FD0EF362553F8C873970B63DA428BD6B66B218A42E555`）和实施计划 `docs\superpowers\plans\2026-09-06-bdd100k-known-blur-quantitative-reproduction.md`（SHA-256=`1B8F44A1B95B6B7CAA58DB22981F6DC25DA390A0912AB0339B6870E70A492C97`）。按计划，权重准备完成前不能进入 Task 10 Step 1，也没有启动 Oracle GPU pilot。
- 只读检查 `DDM4IP-Task10-DRUNet-Weights-v2`：任务已为 `Ready`，`LastTaskResult=1`；运行根 `D:\DDM4IP-runtime\weights\task10-drunet-download-20260907-v2\status.json` 为 `FAILED`，`step=download`，更新时间为 `2026-09-07T18:09:05.3265757+08:00`。
- 失败日志记录下载目标 `D:\DDM4IP-runtime\torch-home\hub\checkpoints\drunet_deepinv_color_finetune_22k.pth` 的 HTTPS/TLS 请求被远端主机关闭（`HttpRequestException` / `SocketException`）。目标文件不存在；在 `D:\DDM4IP-runtime\torch-home` 和 `D:\DDM4IP-runtime\xdg-cache` 下也未找到 `drunet*.pth` 候选文件，因此没有可记录的目标文件大小或 SHA-256。

### 结论与边界

- Task 10 未启动的直接原因尚未解决：DRUNet 预训练权重仍不在 D 盘离线缓存中。`Ready` 状态和下载任务曾运行不能视为成功；当前仍停在“权重准备失败”而不是“Oracle 可运行”。
- 本轮未重试外部下载，未改写或清理 v2 失败运行根，未运行项目训练/评估/GPU 推理，也未注册新的 Oracle 计划任务。v2 的 `status.json`、`task.log`、`status-history.jsonl` 和任务结果保留为诊断证据。

### 下一准入条件

- 需要在新的、单独授权的权重准备阶段把精确文件落到上述目标路径，并独立记录文件大小与 SHA-256；随后在 `HF_HUB_OFFLINE=1`、`TRANSFORMERS_OFFLINE=1` 下实际构造 DRUNet/DPIR，确认不发生网络访问且构造通过。
- 只有上述离线权重门通过后，用户才可在新对话中再次明确授权 Task 10 Oracle GPU pilot；本条记录不授权任何下载重试、Oracle、Step 1/2 训练或正式评估。

## 2026-09-07：Task 10 Step 1 DRUNet 权重下载已由计划任务启动（等待完成）

### 本阶段结果与边界

- 本轮按 `AGENTS.md` 完成启动核验：远端主机为 `DESKTOP-KBM1345`，仓库为 `D:\Unsupervised Imaging Inverse Problems`；远端工作区既有修改和未跟踪文件均保留，未执行 Git 写操作。
- 在 DeepInv `0.4.2` 固定环境中确认：`DRUNet(pretrained="download")` 需要 `drunet_deepinv_color_finetune_22k.pth`；DPIR 是使用该 DRUNet 先验的求解器，没有第二个独立的 DPIR 权重文件。目标文件原先不存在，D 盘缓存中未发现候选权重。
- 经用户本阶段授权，已创建并启动计划任务 `DDM4IP-Task10-DRUNet-Weights-v2`。运行根为 `D:\DDM4IP-runtime\weights\task10-drunet-download-20260907-v2`，目标为 `D:\DDM4IP-runtime\torch-home\hub\checkpoints\drunet_deepinv_color_finetune_22k.pth`；启动确认时任务为 `Running`，`LastTaskResult=267009 (0x41301)`，远端下载进程存在，状态为 `RUNNING`。
- 下载使用 D 盘项目专用临时目录、缓存、日志和状态；本轮未启动 Oracle GPU pilot、Step 1/2 训练、正式评估或任何后续 Task。旧的 v1 失败运行根保留为诊断证据，未覆盖或清理。

### 下一步准入

- 用户可在组内电脑 PowerShell 中查看任务、状态和日志；任务变为 `SUCCESS` 后，再在新的对话中由助手独立核验目标路径、文件大小、SHA-256，并在 `HF_HUB_OFFLINE=1`、`TRANSFORMERS_OFFLINE=1` 下实际构造 DRUNet/DPIR。该独立核验完成前，不得启动 Oracle pilot。

## 2026-09-07：Task 10 Oracle GPU pilot 准入阻塞（未启动）

### 启动与准入核验

- 本轮按本机 `AGENTS.md` 完成启动核验：通过 `ssh group-pc` 确认远端主机为 `DESKTOP-KBM1345`，实际仓库为 `D:\Unsupervised Imaging Inverse Problems`；远端分支为 `main`。远端工作区继续保留用户既有 `AM WORKLOG.md`、已修改代码和未跟踪 synthetic 文件，未执行 Git 写操作。
- 本机 `WORKLOG.md` 与远端版本不一致；远端 `WORKLOG.md` 是更新的 107 行版本，哈希为 `27CECB457D4F0E9A506FB72032859B7D24F0F9E3D1D8A7D5F3407CFB5640C7AE`。本轮以远端日志为准，并未覆盖本机控制日志。
- 已完整读取批准的设计 `docs\superpowers\specs\2026-09-06-bdd100k-known-blur-quantitative-reproduction-design.md`（SHA-256=`6238E075F8FB37F5823FD0EF362553F8C873970B63DA428BD6B66B218A42E555`）和实施计划 `docs\superpowers\plans\2026-09-06-bdd100k-known-blur-quantitative-reproduction.md`（SHA-256=`1B8F44A1B95B6B7CAA58DB22981F6DC25DA390A0912AB0339B6870E70A492C97`）。本轮授权仅覆盖 Task 10 Oracle GPU pilot，未进入任何后续 Task。
- 新鲜只读状态显示 benchmark 根 `D:\DDM4IP-runtime\synthetic-benchmarks\bdd100k-motionblur-v1` 存在且 `status.json` 为 `SUCCESS`，角色计数为 `1000/100/500/139`；Oracle pilot 运行根不存在，同名 Oracle 计划任务未注册。

### Task 10 Step 1 离线权重门结果

- 在固定项目环境 `E:\Anaconda3\envs\ddm4ip\python.exe` 中设置 `HF_HUB_OFFLINE=1`、`TRANSFORMERS_OFFLINE=1`、`TORCH_HOME=D:\DDM4IP-runtime\torch-home` 和 `XDG_CACHE_HOME=D:\DDM4IP-runtime\xdg-cache` 后，实际检查 DeepInv 0.4.2 的 DRUNet 构造路径。
- DRUNet 期望的本地文件为 `D:\DDM4IP-runtime\torch-home\hub\checkpoints\drunet_deepinv_color_finetune_22k.pth`，该文件不存在，相关 D 盘缓存中也未发现 DRUNet 权重。
- 实际 `DRUNet(pretrained="download")` 构造在网络下载调用处被预先阻断，确认它尝试访问 `https://huggingface.co/deepinv/drunet/resolve/main/drunet_deepinv_color_finetune_22k.pth?download=true`；本轮未发起网络访问。

### 结论、边界与下一准入

- Task 10 Step 1 离线先决条件不满足，因此按实施计划停止；没有创建 Oracle pilot 运行根，没有注册或启动计划任务，没有运行 GPU 推理，也没有进入 Step 1/2 训练、正式评估或 Task 14。
- 需要用户在新对话中单独明确授权“准备/下载 Task 10 所需预训练权重”后，才能把权重落到 D 盘项目缓存并重新执行离线构造门；权重就绪后仍需再次在新对话明确授权启动 Oracle GPU pilot。本记录不授权任何后续 Task。

## 2026-09-07：Task 9 Build provenance 修复并完成独立验收

### 根因与修复

- 根因已复现：`scripts\bdd100k_synthetic_runner.py` 的成功路径只为 `inventory` 写 `artifacts.json`；`build` 只写 `command.json`/`status.json`，没有冻结 benchmark 与 inventory 的 provenance，也没有追加 `RUNNING`/终态到 `status-history.jsonl` 和 `task.log`。
- `ddm4ip\benchmarks\bdd100k_synthetic.py` 的未来构建摘要原先缺少 `split_manifest_sha256`、`pairs_manifest_sha256`、`preprocessing_sha256`、`degradation_sha256`。已补充 builder 输出字段；没有重跑或改写现有 benchmark。
- runner 新增 build provenance artifact、只读 `mode=audit` 路径、运行状态/日志记录和不覆盖校验。修复后 SHA-256：runner=`84AC9B1A8B00ED1ECC5940A7E997B638AAECAD5E31C0E432647EFE063B7A22B2`，builder=`135ADC92FFBAB6D1C1EB87A885482951453D6A96F5E7665981316648D7908082`；新增回归测试 SHA-256：runner=`18AF24DFB9BDC278B5B9A9C783A71200C26B12EA2A982CE0284CF6F474C925EE`，builder=`5AFDC7C566CB4B9B19F289BCA709B4CD82BA3B05F725F044E3A69FD8EB07130D`。
- TDD 红灯分别确认缺少 summary 字段和 `write_build_artifacts`；绿灯聚焦套件 `18/18`，完整远端 `unittest discover -s tests -v` 为 `51/51`、退出码 `0`；四个 synthetic Hydra 实际模块入口解析均退出码 `0`。

### Provenance audit 与独立验收

- 未触碰旧 Build 运行根或 benchmark 根。新计划任务 `DDM4IP-BDD100K-SYNTH-Build-Provenance-Audit-v1` 的运行根为 `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-build-provenance-audit`，`LastTaskResult=0`、状态 `SUCCESS/exit_code=0`；其历史为 `RESERVED -> RUNNING -> SUCCESS`，日志记录了开始和结束。
- 新 `artifacts.json` SHA-256=`c5afc7bafe3061a01c1af929e9c555ae04006b56223ab9174c1d6c712417187f`，冻结 inventory manifest 路径、SHA、1,739 条记录、`train/val=1565/174`，并记录 benchmark 8 个文件哈希。现有 benchmark 的 summary/pairs/kernel SHA-256 分别为 `97f874e8497f4f8fb2c814b814c15e3c43cc736afc344df449e58c99d58a346e`、`3c86e1b8cc419e6fdb627eb60d7c6dd209015123eec44f790d0115b39bfff9e4`、`4e292ca42c026965ef9b6d16cacec83091dfc2e461c2c6788c6fdc690f832a7a`。
- 独立只读验收脚本退出码 `0`、报告 `PASS`：源 ID/SHA 唯一且无跨角色重叠；角色计数 `1000/100/500/139`；输出 PNG 均为 `256x256 RGB`；test/dev pairs 的路径、哈希、ID、noise seed 一一匹配；`kernel-gt.pt` 为 `1x1x32x32`、有限、非负、归一化，tensor SHA-256=`c9b12867ce2b271084b1a48cf871bd0585addf23c7fec2d755f0d136f6495c11`；固定样本按项目 motion-blur 物理算子与记录 seed 重放后像素一致。
- 旧 Build 运行根仍保留单条 `RESERVED` history 和原始 `task.log`，没有伪造或补写旧证据；现有 benchmark `summary.json` 仍保持原样（缺少新增字段），这些字段由新的外部 provenance artifact 记录，未来 builder 才会在新目标中写入。

### 边界与下一步

- 本阶段只处理 Build provenance 并完成数据/追溯独立验收；没有启动 Oracle、pilot、Step 1/2 训练或评估，也没有下载权重。按规则，旧 RESERVED Build 运行根继续作为诊断历史保留，不把它改写成成功证据；后续阶段仍需用户在新对话中单独授权。
- 本阶段新增项目专用临时验收脚本：`D:\DDM4IP-runtime\temp\task9_build_provenance_acceptance_20260907.py`，以及其 `PYTHONPYCACHEPREFIX`/matplotlib 临时输出目录；未删除，清理时按精确路径处理。

## 2026-09-07：Task 9 benchmark 数据独立验收通过，编排证据缺口待闭合

### 启动核验与文档

- 已完整读取本机 `WORKLOG.md`，通过 `ssh group-pc` 核验远端主机名为 `DESKTOP-KBM1345`，真实仓库为 `D:\Unsupervised Imaging Inverse Problems`；远端分支为 `main`，Git 状态仍保留用户既有 `AM WORKLOG.md`、已修改代码和未跟踪 synthetic 文件，未执行 add、commit、push、pull、rebase 或分支切换。
- 已完整读取已批准设计与实施计划；设计 SHA-256=`6238E075F8FB37F5823FD0EF362553F8C873970B63DA428BD6B66B218A42E555`，计划 SHA-256=`1B8F44A1B95B6B7CAA58DB22981F6DC25DA390A0912AB0339B6870E70A492C97`。

### 新鲜 Task 9 状态

- 远端 `D:\DDM4IP-runtime\synthetic-benchmarks\bdd100k-motionblur-v1` 已存在，`status.json` 为 `SUCCESS`，Build 计划任务 `DDM4IP-BDD100K-SYNTH-Build-v1` 为 `Ready`、`LastTaskResult=0`；没有 synthetic runner 进程。当前只做核验，未启动 Oracle、pilot、Step 1/2 训练或评估。
- Build 运行根 `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-build` 的 `status.json` 为 `SUCCESS/exit_code=0`，但该运行根没有 `artifacts.json`，`status-history.jsonl` 仍只有 `RESERVED`，`task.log` 仍为 `reserved; execution has not started`。因此不能把 Scheduled Task 编排证据写成完整闭合。

### 独立数据验收结果

- 远端只读验收脚本逐项核对通过：源清单 1,739 条；角色计数 `step1_observation=1000`、`step2_clean=100`、`test_paired=500`、`dev_reserve=139`；所有 PNG 为 256×256 RGB；源清单 1,739 个 ID 和内容 SHA 唯一；跨角色 ID/SHA 无重叠；test/dev pairs 的 ID、路径、源/派生 SHA 和 noise seed 一一匹配。
- source manifest SHA-256=`c3893e937ab6fd38748473e85cf26137991b8a675080414d078bc13cc1861edf`；split manifest SHA-256=`c4c1ffd47ee087e8105eb961226e3058ec96739c8d79ae30c7bbee9d1156742f`；test pairs SHA-256=`3c86e1b8cc419e6fdb627eb60d7c6dd209015123eec44f790d0115b39bfff9e4`；dev pairs SHA-256=`482277fd47d395b369a5c0e53e3bb7d7006133f8d819de0501e878e6f8395530`。
- `kernel-gt.pt` 形状为 `1×1×32×32`，有限、非负且归一化；kernel file SHA-256=`4e292ca42c026965ef9b6d16cacec83091dfc2e461c2c6788c6fdc690f832a7a`；tensor SHA-256=`c9b12867ce2b271084b1a48cf871bd0585addf23c7fec2d755f0d136f6495c11`。用同一源图、项目 `motion_blur` 物理算子和记录的 noise seed 重放，生成 noisy PNG 哈希一致。
- `summary.json` 当前缺少计划所要求的 `split_manifest_sha256`、`pairs_manifest_sha256`、`preprocessing_sha256`、`degradation_sha256` 字段；本次验收哈希已记录在本日志，未修改 benchmark 文件或补写字段。
- 本次只读验收产生的项目专用临时清理项为 `D:\DDM4IP-runtime\temp\benchmark_verify_20260907.py` 和 `D:\DDM4IP-runtime\temp\benchmark-verify-20260907`（含本次进程的 `PYTHONPYCACHEPREFIX`/matplotlib 输出）；未删除目录，需后续由用户按精确路径清理。

### 结论、边界与下一步

- 结论应分开表述：benchmark 像素和数据内容已生成，且独立数据验收通过；Task 9 的运行器/工件追溯证据尚未闭合，不能宣称整个 Task 9 已无条件完成。
- 本轮没有启动任何训练。按照设计与计划，必须先处理/明确 Build provenance 缺口，再在新对话单独授权 Task 10 Oracle GPU pilot；Oracle 通过后，Step 1 pilot/full、Step 2 pilot/full 仍需分别新对话和明确授权，不能由本轮泛化授权替代。
- 后续处理不得覆盖 benchmark 根、现有真实 BDD100K 主线或历史实验目录；不得用 `status.json=SUCCESS` 单独替代独立验收，也不得把 `RESERVED` 的 Build 运行根改写为成功证据。

## 2026-09-06：按用户确认启动 synthetic benchmark 构建（Task 9 进行中）

### 启动、失败与修复

- 用户明确澄清：benchmark 尚未构建时应继续把它构建。本阶段据此授权执行 Task 9；未授权 Oracle GPU pilot、训练或评估。
- 重新通过 `ssh group-pc` 确认主机为 `DESKTOP-KBM1345`。Task 9 inventory v1 首次执行因 runner 子进程未注入仓库根 `PYTHONPATH` 失败，实际复现为 `ModuleNotFoundError: No module named 'ddm4ip'`；失败 run root `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-inventory` 和任务 `DDM4IP-BDD100K-SYNTH-Inventory-v1` 均保留作为诊断证据，未覆盖。
- 采用测试先行增加 `test_child_process_environment_includes_project_root`：修复前 runner focused suite 为 11 个测试、1 个错误；增加 `child_process_environment()` 并让 runner 的子进程显式继承仓库根 `PYTHONPATH` 后，focused suite 为 11/11，完整远端无训练套件为 50/50，builder `--help` 在同等环境下退出码 0。修复后 runner SHA-256=`FA01C56F08F953C6254A46B78AC150F8DDF03472E3E10725180FB3694CFE10BF`；新增测试文件 SHA-256=`3DA5BE92264EDAE6E5EAADFD0E6B80F18F49D1C358577A4435A24A148477C4FA`。

### Inventory 独立验收

- v2 inventory 通过任务 `DDM4IP-BDD100K-SYNTH-Inventory-v2` 运行，run root 为 `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-inventory-v2`；计划任务退出码 0，`status=SUCCESS`。
- 独立验收通过：source manifest SHA-256=`c3893e937ab6fd38748473e85cf26137991b8a675080414d078bc13cc1861edf`；记录数、唯一 source ID、唯一内容 SHA 均为 1,739；来源计数为 `train=1565`、`val=174`；全部 `1280×720×3`；1,739 个源文件均存在。`artifacts.json` SHA-256=`04D03CED8430AF91944A85D5C402E09ACC381AFFF2D69770343C1B647EFFEB61`。

### Benchmark build 当前状态

- 已依据经过独立验收的 `artifacts.json` 生成 build spec，并通过正式 launcher 启动任务 `DDM4IP-BDD100K-SYNTH-Build-v1`；run root 为 `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-build`，目标 benchmark 根为 `D:\DDM4IP-runtime\synthetic-benchmarks\bdd100k-motionblur-v1`。
- 启动确认时 `LastTaskResult=267009`（`0x41301`，表示仍在运行），状态文件为 `RESERVED`，benchmark 根已创建并开始写入；这只能证明任务正在执行，不能声明 benchmark 已完成。必须等用户报告结束后，在新的 SSH 进程中独立验收角色计数、PNG/配对、固定核、清单和哈希。
- 当前阶段没有启动 Oracle、权重下载、GPU pilot、Step 1/2 训练或 Step 3 评估。保留失败 v1 inventory、成功 v2 inventory、build run root、输入 spec、launcher 日志和计划任务，供后续复核与清理清单使用。

## 2026-09-06：启动核验确认 benchmark 尚未构建（本轮只更新日志与规则）

### 本轮核验

- 已按本机 `AGENTS.md` 完成启动核验：完整读取本机 `WORKLOG.md`，通过 `ssh group-pc` 确认主机名为 `DESKTOP-KBM1345`，远端仓库为 `D:\Unsupervised Imaging Inverse Problems`，分支为 `main`；远端工作区仍保留既有 `AM WORKLOG.md`、Task 1–8 代码/测试及未跟踪 synthetic 文件，本轮未执行 Git 写操作。
- 已完整读取已批准设计 `docs\superpowers\specs\2026-09-06-bdd100k-known-blur-quantitative-reproduction-design.md`（SHA-256=`6238E075F8FB37F5823FD0EF362553F8C873970B63DA428BD6B66B218A42E555`）和实施计划 `docs\superpowers\plans\2026-09-06-bdd100k-known-blur-quantitative-reproduction.md`（SHA-256=`1B8F44A1B95B6B7CAA58DB22981F6DC25DA390A0912AB0339B6870E70A492C97`）。设计和计划均明确：Task 9 数据 inventory 与 benchmark 构建需要单独授权，且 inventory 验收后还要再次批准才可写入 benchmark 像素。
- 新 SSH 进程的只读状态确认：`D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-inventory`、`D:\DDM4IP-runtime\synthetic-benchmarks\bdd100k-motionblur-v1` 和正式 experiment 根均不存在；`SYNTH_TASK_COUNT=0`；源视图仍为 `train\clean=1565`、`val\clean=174`，`manifest.csv` SHA-256=`6BA1F476AFAEFACA60A9B6EDFB7DB2740BF99D355C12F49335FFB6C342724886`。

### 结论与边界

- benchmark 构建没有完成，也没有开始：未扫描正式 1,739 张源图，未生成 inventory、PNG、固定核、pairs manifest 或 benchmark 像素，未注册/启动计划任务，未下载权重，未运行 GPU pilot、训练或评估。
- 本轮只更新本机长期规则和本远端工作日志；不把 Task 1–8 的代码/无训练测试、runner 前置修复、Hydra 解析或夹具验证写成 benchmark 已完成。
- 下一准入仍为：新对话中用户明确授权 Task 9 的 inventory-only；独立验收 `artifacts.json`、source manifest hash、1,739 个唯一 source ID/SHA、`1565/174` 来源计数及 `1280×720 RGB` 后停止，等待再次明确批准才构建 benchmark；benchmark 独立验收后才可另行授权 Task 10 Oracle GPU pilot。

## 2026-09-06：修复 Task 9 synthetic runner 前置阻塞（未运行数据构建）

### 启动核验与根因

- 本阶段重新完成 `AGENTS.md` 启动核验：`ssh group-pc` 主机名为 `DESKTOP-KBM1345`，真实仓库为 `D:\Unsupervised Imaging Inverse Problems`，分支为 `main`；远端工作区保留既有 `AM WORKLOG.md`、Task 1–8 代码/测试和未跟踪文档，未执行 Git 写操作。
- 当前远端 `WORKLOG.md` 修改前 SHA-256 为 `642DC94F8B030B65C8EC094FE1AC423ADFA38DF71A0C5BADF900B8901D72739E`；已完整重读批准的设计 `6238E075F8FB37F5823FD0EF362553F8C873970B63DA428BD6B66B218A42E555` 和实施计划 `1B8F44A1B95B6B7CAA58DB22981F6DC25DA390A0912AB0339B6870E70A492C97`。
- 使用已有 runner 夹具稳定复现 wrapper 失败：`start_bdd100k_synthetic_task.ps1` 把外部 spec 文件路径原样传给 execute，synthetic runner 将其当作运行目录，实际寻找 `...\spec.json\spec.json` 并退出码 1。
- 对照既有 `bdd100k_runner.py` 确认正确契约是：prepare 读取外部 spec 文件并生成 `run_root\spec.json`，Scheduled Task execute 必须传入这个保留 spec 文件；不能继续传外部 spec，否则缺少 `runner_sha256/reserved_at`。
- Task 9 Step 4 的第二个阻塞也已确认：inventory CLI 只写 `source-manifest.csv`，runner 原先只写 `command.json/status.json`，不会生成计划要求的 `artifacts.json`；同时 build 分支原先固定从 build run root 查找 manifest，无法接收 inventory 产物。

### 修复内容

- `scripts\bdd100k_synthetic_runner.py` 现在同时接受 spec 文件和 run root，按保留 spec 的父目录解析 run root，并校验 spec 中的 `run_root` 与实际路径一致。
- inventory 成功后写出 `artifacts.json`，冻结 `source_manifest.path`、文件 SHA-256、记录数、唯一 source ID/内容 SHA 数量以及 `train`/`val` 来源计数；不改变 builder 的源图扫描和 benchmark 生成逻辑。
- build spec 新增受 schema 允许的 `source_manifest` 字段，命令显式使用经过 inventory 验证的 manifest 路径；路径限制在 `D:\DDM4IP-runtime\experiments` 下。
- `start_bdd100k_synthetic_task.ps1` 在 prepare 后读取外部 spec 的 `run_root`，只把新生成的 `run_root\spec.json` 传给 Scheduled Task execute。旧的 real-data runner 未修改。
- 修改后文件 SHA-256：runner=`C225CB208F8670249416DFEE1282F5D07F90CB5C78600416A93BBECE748A0F27`；launcher=`B000A17D08ED09C5F3E9E271120F9DECB47FC07389181E0447C47A9D4034F084`；schema=`12EFB988A468FD71163E2D557DF4468A11DFC3E0A808B26341C64AB5E0019F9F`；runner test=`A647020387F7DD4BCE814B9BAFCD024A6A541C626E3739511C02105215C3462B`。

### TDD 与独立验证

- 先上传失败回归测试并在修复前确认：spec 文件路径测试报 `...\spec.json\spec.json`，inventory artifacts 测试报缺少 `write_inventory_artifacts`，build handoff 测试报未知 `source_manifest`，wrapper 契约测试失败；退出码 1。
- 修复后 `E:\Anaconda3\envs\ddm4ip\python.exe -m unittest tests.test_bdd100k_synthetic_runner -v`：10/10 通过，退出码 0。
- PowerShell wrapper parser：`start_bdd100k_synthetic_task.ps1` 和 `run_bdd100k_synthetic_stage.ps1` 均 `parse_errors=0`；schema `ConvertFrom-Json` 成功且含 `source_manifest`。
- 完整远端 `python -m unittest discover -s tests -v`：49/49 通过，退出码 0；四个实际模块入口 `step1_bdd100k_synthetic`、`step2_bdd100k_synthetic`、`step3_bdd100k_oracle`、`step3_bdd100k_synthetic` 的 Hydra `--cfg job --resolve` 均退出码 0。
- 独立只读门禁确认 `SYNTH_TASK_COUNT=0`、benchmark 根不存在、正式 experiment 根不存在；本阶段未注册/启动计划任务，未扫描正式源图、未生成 benchmark 像素、未下载权重、未运行 GPU pilot 或 Task 10。

### 当前边界、清理清单与下一步

- Task 9 inventory/build 仍未执行，`D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-inventory` 和 `D:\DDM4IP-runtime\synthetic-benchmarks\bdd100k-motionblur-v1` 均不存在。Task 10 不能从本阶段直接开始。
- 本阶段无训练门禁日志目录：`D:\DDM4IP-runtime\temp\bdd100k-synthetic-hydra-resolve-task9-fix-20260906`，本项目独占，用户可在后续清理时删除该明确目录；未删除任何文件。
- 下一阶段准入仍是：在新对话重新启动核验后，用户明确授权 Task 9 inventory-only；先通过 launcher 生成并独立验收 `artifacts.json` 与 source manifest hash，等待再次明确批准后才构建 benchmark；完成并独立验收 benchmark 后，才能另行授权 Task 10 Oracle GPU pilot。

本文件用于按日期记录项目环境、实验过程、代码修改、运行结果和后续计划。新增记录时在文件顶部日期之后继续追加，重要命令和结果尽量保留，便于复现与排查问题。

## 2026-09-06：完成已批准的实施计划 Task 1–8（代码与无训练测试）

### 启动核验与边界

- 本阶段按 `AGENTS.md` 重新完成启动核验：`ssh group-pc` 的远端主机名为 `DESKTOP-KBM1345`，远端目录为 `D:\Unsupervised Imaging Inverse Problems`，分支为 `main`，远端 Git 状态为 `## main...origin/main` 加既有脏文件；本阶段未执行 `git add`、提交、推送、拉取、变基或切换分支。
- 启动时远端 `WORKLOG.md` SHA-256 为 `2F1815DBAB110DC0B01D539F47236407D507A26222E0DF3539E521403A6EE762`。设计文件 SHA-256 为 `6238E075F8FB37F5823FD0EF362553F8C873970B63DA428BD6B66B218A42E555`，实施计划 SHA-256 为 `1B8F44A1B95B6B7CAA58DB22981F6DC25DA390A0912AB0339B6870E70A492C97`。
- 严格只执行本次授权的 Task 1–8；未执行 Task 9 或后续的数据扫描、benchmark 生成、计划任务注册/启动、模型权重下载、GPU pilot、Step 1/2 训练和正式评估。旧的 `D:\DDM4IP-runtime\orchestration\bdd100k_runner.py` 未修改。

### Task 1–8 完成情况

- Task 1：增加 `.pt` 已知 kernel 加载和 `file_blur` 配置，保留 `.mat` 路径并校验形状、有限性、非负性和归一化。
- Task 2：增加源图 inventory 记录、SHA-256 清单和确定性 1000/100/500/139 split。
- Task 3：增加固定中心裁剪、256×256 bicubic 预处理、稳定 motion kernel、固定噪声种子和拒绝覆盖的 synthetic benchmark builder/CLI；仅使用小型确定性夹具验证，未扫描正式 BDD100K。
- Task 4：增加严格 JSONL `manifest_paired` 数据集及 clean/noisy 单侧读取边界，拒绝不安全路径、重复 source、错误哈希和错误尺寸。
- Task 5：增加标量 PSNR/SSIM/LPIPS、kernel PSNR/NCC、确定性 metrics writer、跨 seed 聚合器和只读 kernel 分析脚本。
- Task 6：增加 quantitative trainer 的 prediction/kernel/manifest/metrics/summary 输出、source 唯一性和拒写已有产物验证。
- Task 7：增加 synthetic runtime、noisy-only、clean-only、manifest-paired、DPIR 和 Step 1/2/3 Hydra 配置；Step 1/2/3 配置契约测试通过。
- Task 8：增加隔离的 `scripts\bdd100k_synthetic_runner.py`、schema、两个 PowerShell wrapper 和 fail-closed 运行器夹具；只解析 wrapper 和运行器测试，未注册或启动 Scheduled Task。修复并验证了 reserved spec 的 `reserved_at` round-trip 兼容性。

### 逐文件修改/新增清单

- Kernel、数据和训练代码：`ddm4ip\degradations\degradation.py`、`ddm4ip\data\base.py`、`ddm4ip\data\patch_dataset.py`、`ddm4ip\data\manifest_paired_dataset.py`、`ddm4ip\losses\deepinv_loss.py`、`ddm4ip\trainers\deepinv_denoiser.py`。
- Synthetic benchmark 与指标：`ddm4ip\benchmarks\__init__.py`、`ddm4ip\benchmarks\bdd100k_synthetic.py`、`ddm4ip\utils\benchmark_metrics.py`、`scripts\build_bdd100k_synthetic_benchmark.py`、`scripts\analyze_bdd100k_synthetic_kernel.py`、`scripts\aggregate_bdd100k_synthetic_results.py`。
- Hydra 配置：`ddm4ip\configs\dataset\degradation\file_blur.yaml`、`ddm4ip\configs\paths\bdd100k_synthetic_runtime.yaml`、`ddm4ip\configs\dataset\bdd100k_synthetic_noisy.yaml`、`ddm4ip\configs\dataset\bdd100k_synthetic_clean.yaml`、`ddm4ip\configs\dataset\bdd100k_synthetic_paired.yaml`、`ddm4ip\configs\models\dpir_bdd100k_256.yaml`、`ddm4ip\configs\exp\step1_bdd100k_synthetic.yaml`、`ddm4ip\configs\exp\step2_bdd100k_synthetic.yaml`、`ddm4ip\configs\exp\step3_bdd100k_oracle.yaml`、`ddm4ip\configs\exp\step3_bdd100k_synthetic.yaml`。
- 测试：`tests\test_file_blur.py`、`tests\test_bdd100k_synthetic_builder.py`、`tests\test_manifest_paired_dataset.py`、`tests\test_bdd100k_synthetic_data_boundaries.py`、`tests\test_noisy_only_patch_dataset.py`、`tests\test_benchmark_metrics.py`、`tests\test_bdd100k_synthetic_trainer.py`、`tests\test_bdd100k_synthetic_configs.py`、`tests\test_bdd100k_synthetic_runner.py`。
- Task 8 运行时文件：`D:\DDM4IP-runtime\orchestration\synthetic-step-spec.schema.json`、`D:\DDM4IP-runtime\orchestration\run_bdd100k_synthetic_stage.ps1`、`D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1`。

### 测试、退出码与关键结果

- Task 1：`python -m unittest tests.test_file_blur tests.test_internal_package_imports -v`，6 tests，退出码 0。
- Task 2/3：`python -m unittest tests.test_bdd100k_synthetic_builder -v`，最终 6 tests，退出码 0。
- Task 4：`python -m unittest tests.test_manifest_paired_dataset tests.test_bdd100k_synthetic_data_boundaries tests.test_noisy_only_patch_dataset -v`，4 tests，退出码 0。
- Task 5：`python -m unittest tests.test_benchmark_metrics tests.test_deepinv_no_reference -v`，6 tests，退出码 0。
- Task 6：`python -m unittest tests.test_bdd100k_synthetic_trainer tests.test_deepinv_no_reference tests.test_step3_geometry_provenance -v`，10 tests，退出码 0。
- Task 7：`python -m unittest tests.test_bdd100k_synthetic_configs -v`，2 tests，退出码 0。
- Task 8：PowerShell Parser 对两个 wrapper 的 `parse_errors=0`，schema `ConvertFrom-Json` 成功；补齐 inventory/build 非 Hydra 分派后，`python -m unittest tests.test_bdd100k_synthetic_runner -v`，7 tests，退出码 0。
- 最终独立门禁：`python -m unittest discover -s tests -v`，46 tests，退出码 0，`OK`。仅有既有 DeepInv deprecation warning，无失败测试。
- 最终四个实际模块入口解析均使用 `python -m ddm4ip.main exp=<...> paths=bdd100k_synthetic_runtime --cfg job --resolve`，退出码均为 0：`step1_bdd100k_synthetic`、`step2_bdd100k_synthetic`、`step3_bdd100k_oracle`、`step3_bdd100k_synthetic`。最后一轮解析日志目录为 `D:\DDM4IP-runtime\temp\bdd100k-synthetic-hydra-resolve-final2-20260906`，对应输出字节数为 3790、4516、2618、2622；未构造数据集、未下载权重、未启动训练或评估。
- 最终只读验收：`SYNTH_SCHEDULED_TASK_COUNT=0`；`D:\DDM4IP-runtime\synthetic-benchmarks\bdd100k-motionblur-v1=False`；`D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1=False`；旧运行器 SHA-256 为 `CF556F72FBFCA5316D9E49048E2A0136700136659AC8F2F86C03B9C45BC81A68`。

### 关键文件 SHA-256

- 代码：`ddm4ip\degradations\degradation.py`=`AE16E48E73CFF427A054690C38D4B7D91D090433933508EFECB12AF3916DC137`；`ddm4ip\data\base.py`=`9629C55C8D5E27DE8A7039AB1FC6FD17D3D9409579C1383A67B289DC8A80E24A`；`ddm4ip\data\patch_dataset.py`=`E93225F09F8AE96EA73E2EB89324D0183C4BECD68BBB2E0AA7900211991F6574`；`ddm4ip\data\manifest_paired_dataset.py`=`E18EC1C9ABA43C2B03FAA62C954B04B374B0406FBE13B6DFDF65B284832B11F9`；`ddm4ip\losses\deepinv_loss.py`=`8B277D4E639A3B72542ADF440A93774746AA4BA680EA5939BC44F58D070F3F2F`；`ddm4ip\trainers\deepinv_denoiser.py`=`A3772AE97557474E6A6FE7F395435F52DE62398CFA51C73B5C4F6F8727F28939`。
- Synthetic 核心：`ddm4ip\benchmarks\bdd100k_synthetic.py`=`0CD2127560780DE81DF5EF39BCC6E382B12278BBA9F75E71BB89C7DBAD4EEB2B`；`ddm4ip\utils\benchmark_metrics.py`=`BB2059023D3F243B577065777B7909441A02CDD2830CA2354FAF7C6FDE4EAAD6`；`scripts\bdd100k_synthetic_runner.py`=`63A379A1C6960A8C9E70DE90772D701AECB50369D06136D9005E6A6F6F17EEF3`。
- 配置：`ddm4ip\configs\dataset\degradation\file_blur.yaml`=`37E4FC61BC942D5F23C5080CCFE2BFB1E5150B10C072796B1FBFB131307469DF`；`ddm4ip\configs\paths\bdd100k_synthetic_runtime.yaml`=`EF1C28F35D284A5CF01F486EFA9276CE383DE203C6D2F735483F185551BDBCF7`；`ddm4ip\configs\exp\step1_bdd100k_synthetic.yaml`=`A14D91F5DB5B9EF220A5166DA418C4A44D6DB91C80708BEE602F3759925C0163`；`ddm4ip\configs\exp\step2_bdd100k_synthetic.yaml`=`2EBC350921F5B533E283354AD5FC4128E902250562DD330D7F31415D7972B549`；`ddm4ip\configs\exp\step3_bdd100k_oracle.yaml`=`FC3D3713AF94085B4E56649FCC30C4C1C28AD04CCE94CA10DFBC6BE3B5279593`；`ddm4ip\configs\exp\step3_bdd100k_synthetic.yaml`=`007DF68651B0086C383F08B085DA4C962FE819AB487FE6C03366B5C940C1FC44`。
- 测试与运行时：`tests\test_bdd100k_synthetic_runner.py`=`8D4309913A0CB6C7B266E05E73378270422E576BA9499E99A03A28A8AFFBC44B`；`tests\test_bdd100k_synthetic_builder.py`=`BE82EB52BD90A0E95AE1955C908C8416DD8D2D0DBCBE7F093A9963B98F037AC5`；`D:\DDM4IP-runtime\orchestration\synthetic-step-spec.schema.json`=`A3188894A5BBE596BCEF15FFC7E5DBD7E6AE28BDDE60F5F3C91E7FCBB1D195D7`；`D:\DDM4IP-runtime\orchestration\run_bdd100k_synthetic_stage.ps1`=`D60A48B3735FD8F7394A1CC2CC01931734F37E2DD24708790317B31967E8DF40`；`D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1`=`588649707F1725271E5F97D8B345DDE6C7BBF91062BA434212C63641ED3902DA`。

### 未解决风险与清理清单

- 未解决风险：本阶段只验证确定性小型夹具和配置解析；未对真实 1,739 张源图、实际 benchmark、DPIR/DRUNet 权重、GPU 推理或 Scheduled Task 执行做验收。真实 BDD100K 审计没有来源组 ID；正式指标仍不能被解释为按视频/采集来源隔离。固定中心裁剪和合成已知退化也仍是设计边界。
- 运行器的 checkpoint/manifest 校验使用序列化夹具验证通过，但真实终点 checkpoint、真实 kernel snapshot 和 500 条评估输出仍需后续阶段独立验收。
- 本阶段产生/保留的项目专用解析日志目录为 `D:\DDM4IP-runtime\temp\bdd100k-synthetic-hydra-resolve-20260906`、`D:\DDM4IP-runtime\temp\bdd100k-synthetic-hydra-resolve-final-20260906` 和 `D:\DDM4IP-runtime\temp\bdd100k-synthetic-hydra-resolve-final2-20260906`；最后一轮测试保留夹具目录包括 `D:\DDM4IP-runtime\temp\base-final-checkpoint-y4f899yi` 和 `D:\DDM4IP-runtime\temp\step3-geometry-sp26g89b`。这些路径仅供本项目复核，未执行删除；通用 `D:\DDM4IP-runtime\temp`、`pip-cache`、`torch-cache`、`xdg-cache` 只作为进程级环境变量使用，未修改全局环境变量。

### Task 9 精确准入条件

- 必须在新对话中重新按 `AGENTS.md` 完成主机、远端 Git、远端 WORKLOG、完整无训练套件和四个 Hydra 解析核验，并由用户明确授权 Task 9 的“真实源清单冻结与 benchmark 构建”阶段；本条记录不能替代新授权。
- 新阶段开始前必须只读核对 `D:\DDM4IP-runtime\group-data-views\BDD100K_Blur_Sharp`，确认源视图计数为 `1,565/174`，view manifest SHA-256 为 `6BA1F476AFAEFACA60A9B6EDFB7DB2740BF99D355C12F49335FFB6C342724886`，且远端数据路径不是重复副本。
- 获得明确授权后，第一步只能通过 `start_bdd100k_synthetic_task.ps1` 创建 inventory-only 规格和计划任务 `DDM4IP-BDD100K-SYNTH-Inventory-v1`；完成后必须在新的 SSH 进程独立验证 SUCCESS、退出码 0、1,739 个唯一 source ID/SHA、1,565/174 source-root 分布和 1280×720 RGB，然后报告冻结的 inventory hash 并停止，等待再次明确批准后才可写入 benchmark 像素。

## 2026-09-06：批准已知模糊定量复现设计并完成实施计划

### 已完成并核验

- 用户已审核并批准 `docs\superpowers\specs\2026-09-06-bdd100k-known-blur-quantitative-reproduction-design.md`。该设计文件的 SHA-256 为 `6238E075F8FB37F5823FD0EF362553F8C873970B63DA428BD6B66B218A42E555`。
- 已按 `writing-plans` 编写逐文件、测试先行的实施计划：`docs\superpowers\plans\2026-09-06-bdd100k-known-blur-quantitative-reproduction.md`。上传后 SHA-256 为 `1B8F44A1B95B6B7CAA58DB22981F6DC25DA390A0912AB0339B6870E70A492C97`；计划共 820 行、14 个 Task、89 个检查项，未发现未替换占位符。
- 计划 Task 1–8 是代码与无训练测试；Task 9 是真实源清单冻结与 benchmark 数据构建；Task 10 是 Oracle GPU pilot；Task 11 是 Step 1 pilot 和正式预算训练；Task 12 是一次 Step 2 pilot 和五个完整随机种子训练；Task 13 是正式 500 图 Oracle 与五个 learned checkpoint 评估；Task 14 是汇总、失败复核和有边界的结果报告。
- 只有 Task 11 和 Task 12 包含训练；两者的 pilot 也属于短训练。Task 10 和 Task 13 使用 GPU 但属于推理/评估，不属于训练。
- 本阶段没有修改项目代码，没有生成真实数据，没有启动 pilot、训练、评估、下载或计划任务。
- 2026-09-06 新对话启动核验再次确认远端主机为 `DESKTOP-KBM1345`、仓库分支为 `main`。更新前 `WORKLOG.md` 工作树文件缺失且状态为 `AD`；本次经用户明确授权，以 Git 索引中的 64 行既有版本为基线恢复并追加本条记录，保留索引内容且不执行 `git add`，因此不改写用户已有暂存区。

### 后续阶段与授权边界

- 下一阶段从实施计划 Task 1 开始。每个新对话必须先按本机 `AGENTS.md` 完成启动核验，完整读取上述设计与计划，并以远端新鲜状态确认前序准入条件。
- 用户可以在新对话提示词中只写“先按 `AGENTS.md` 完成完整启动核验”，无需重复列出读取本机日志、SSH 主机名核验、远端 `git status` 和远端日志检查四个子步骤；四项规则仍保留在 `AGENTS.md` 中，不得从项目规则删除。
- 每次授权只覆盖用户明确指定的 Task 或阶段。代码与无训练测试、数据构建、Oracle pilot、Step 1 pilot、Step 1 full、Step 2 pilot、Step 2 full、Step 3 正式评估和结果复盘应继续分阶段授权；pilot 通过不自动授权 full，训练完成不自动授权评估。

## 2026-09-01：建立远程开发工作流

### 工作目标

- 在本地电脑使用 VS Code 查看和编辑代码。
- 通过 Remote SSH 连接组里电脑 `group-pc`。
- 依赖安装、训练和测试均在组里电脑上执行。
- 在 VS Code 中完成 Git 状态检查、提交和推送等操作。

### 已完成

- 确认远端主机名为 `DESKTOP-KBM1345`，操作系统为 Windows。
- 确认远端仓库路径为 `D:\Unsupervised Imaging Inverse Problems`。
- 确认仓库当前分支为 `main`，创建本日志前工作区干净。
- 配置 VS Code Remote SSH 主机 `group-pc`，远端平台设置为 `windows`。
- 信任远端工作区并成功连接仓库。
- 定位首次连接失败原因：Remote SSH 使用 17 秒连接超时，而远端 PowerShell/VS Code Server 首次响应可能超过 30 秒。
- 在本地 VS Code 用户设置中加入以下配置，将超时提高到 60 秒：

```json
"remote.SSH.connectTimeout": 60
```

### 当前工作方式

- VS Code 窗口和键盘操作发生在本地电脑。
- 资源管理器中显示的是远端仓库文件。
- Remote SSH 窗口中新建的终端运行在组里电脑上。
- `pip`、`conda`、Python、CUDA、训练和测试命令均使用组里电脑的环境与硬件。
- VS Code 源代码管理面板操作的是远端仓库。

### 网络与延迟

- 本地电脑需要保持香港 VPN 节点，以便使用 Codex。
- VPN 可能使 SSH 流量绕行，从而增加 VS Code Remote SSH 的输入和文件访问延迟，但它不是目前唯一的延迟来源。
- 已测得普通 SSH 命令可以成功执行；远端 PowerShell/VS Code Server 的启动也存在明显等待。
- 暂不关闭 VPN。后续可在 VPN 客户端中为 `Code.exe`、`ssh.exe` 或 `group-pc` 的地址配置直连/绕过代理，以同时保留 Codex 和低延迟 SSH。

### 连接验证命令

在 VS Code Remote SSH 终端中运行：

```powershell
hostname
Get-Location
git status
nvidia-smi
```

预期主机名为 `DESKTOP-KBM1345`，当前位置为远端仓库目录。

### 下一步

- 检查远端 Python、Conda、CUDA、PyTorch 和 GPU 环境。
- 阅读仓库说明和依赖文件，确定推荐的环境创建方式。
- 创建独立项目环境并安装依赖。
- 找到训练、测试入口以及数据集和配置文件的位置。
- 运行最小测试，确认代码、CUDA 和数据读取正常。
- 确定实验命名、输出目录、模型权重和日志的保存规范。

## 2026-09-08：Phase C kernel hash 修正与 Oracle pilot v3 启动（未完成）

### 本轮授权与边界

- 用户明确授权本轮完成 Phase C Oracle GPU pilot，包括 kernel hash 大小写修复、TDD 回归、无训练门禁、创建并启动一个新的 16 图 `dev_reserve` Oracle Scheduled Task；明确禁止 Step 1/2/3 训练、正式 500 图 learned-checkpoint 评估、下载新模型、重建 benchmark 和修改实验设计。
- 本轮没有执行 git add/commit/push/pull/rebase/reset 或分支切换；保留远端既有脏工作树及 v1/v2 失败运行根。

### TDD 修复与无训练验收

- 新增远端测试 `tests\test_kernel_hash_canonicalization.py`，SHA-256=`3BAE69E2CB1B1CF4DE958CF56A25CC476FC97668EBF15DE9704E233B84A9D9A8`。旧代码红灯证据为 `D:\DDM4IP-runtime\temp\phaseC-kernel-hash-red-20260908\red.log`，SHA-256=`F77183866ECFF57389C9F8599CB2597CE7736EF06FC5175C095D3AA7080154FE`，退出码 `1`，`deepinv_denoiser.py:317` 报 `ValueError: configured kernel_gt_sha256 does not match kernel_gt_path`。
- 对 `ddm4ip\trainers\deepinv_denoiser.py` 只做最小修复：比较两侧 hash 时使用大小写不敏感的字符串比较；磁盘文件和 `MetricWriter` 输出仍保持 lowercase canonical SHA-256。修复后文件 SHA-256=`AC6BE58FF10F5AF5AE662227E640507D27754C4744217BED4E5D6D41FEEAA0A7`；同一回归绿灯 `1/1`、退出码 `0`。
- Phase C preflight 运行根 `D:\DDM4IP-runtime\temp\phaseC-preflight-20260908-v5`：聚焦测试 `37/37`、退出码 `0`（日志 SHA-256=`B145EE270745EACC139340B90D265AD1091AFAED833A6095432263D0BC66DDE7`）；完整 `unittest discover` `68/68`、退出码 `0`（日志 SHA-256=`BE96D30466966514FBFEC032BAF257202B7BF268979D0A47946A8798AEBB98C8`）；四个 synthetic Hydra `--cfg job --resolve` 均退出码 `0`。汇总 `preflight-summary.json` SHA-256=`1D35E73935E179BF545207A418D34AB2BFD0D93DE2D8EB45221857A7425FF5AA`。
- 离线模型门禁继续只使用 D 盘既有缓存：AlexNet `D:\DDM4IP-runtime\torch-home\hub\checkpoints\alexnet-owt-7be5be79.pth`，244408911 字节，SHA-256=`7be5be791159472b1fbf3c69796f7cb30dca7ad8466c2df70058c37116cdee02`；DRUNet `D:\DDM4IP-runtime\torch-home\hub\checkpoints\drunet_deepinv_color_finetune_22k.pth`，130585443 字节，SHA-256=`20296845d272d3d786b89ea3c1208d5f2ceb57658a499d4dd28073cbb73508aa`。LPIPS/DRUNet/DPIR 离线实际构造通过，network guard hits=`0`；`offline-result.json` SHA-256=`C5E4D81E3506C787FE45E14009B738D166172273D02BEFC225BA091B12B3A803`。
- 启动前 benchmark 输入未改写且哈希复核通过：summary=`97F874E8497F4F8FB2C814B814C15E3C43CC736AFC344DF449E58C99D58A346E`、`dev-reserve/pairs.jsonl`=`482277FD47D395B369A5C0E53E3BB7D7006133F8D819DE0501E878E6F8395530`、`degradation/kernel-gt.pt`=`4E292CA42C026965EF9B6D16CACEC83091DFC2E461C2C6788C6FDC690F832A7A`。

### Phase C v3 调度证据

- 新 external spec `D:\DDM4IP-runtime\experiments\phaseC-oracle-pilot-spec-20260908-v3.json`，SHA-256=`0C8B58C2E31ADA8F265C98DBE3DBE48068E03A9D691D6B12059072BDC56C2766`；spec 固定 `stage=oracle`、`mode=pilot`、`variant=oracle`、无 seed/predecessor、`dataset.test.max_imgs=16`、`expected_manifest_records=16`、`pairs_manifest=dev-reserve/pairs.jsonl`。runner `scripts\bdd100k_synthetic_runner.py` SHA-256=`9ED9344827D11A051AD60416A4E9F8085A9026D89105C15E48F76510CE4C8710`。
- 通过 `start_bdd100k_synthetic_task.ps1` 成功注册并启动新任务 `DDM4IP-BDD100K-SYNTH-Oracle-Pilot-v3`；launcher log 为 `D:\DDM4IP-runtime\experiments\phaseC-oracle-pilot-launch-20260908-v3.log`，SHA-256=`24DCD73B4767B9170FBF174A85BAF2E9B0CEC0381BD0F2693A7B36EC720D7DCC`，launcher 退出码 `0`。reserved spec 已落在全新 run root `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot-v3`，未覆盖 v1/v2。
- 启动后独立快照：Scheduled Task=`Running`，`LastTaskResult=267009 (0x41301，表示仍在运行)`；run root、`status.json`、`status-history.jsonl`、`task.log` 均存在；状态已从 `RESERVED` 更新为 `RUNNING`，runner 与 `ddm4ip.main` 子进程均存在。快照时 status SHA-256=`C1A2EB6E6A1F64A1C40C5D36CB8106839330E379F7F452616584012A8A0A8219`，history SHA-256=`E84935C88B0BEF51545C1DFF0319ACC6E5714F2E3FD71597012597D8A6F2B430`。
- 本条只记录 v3 已托管并正在执行；截至该快照尚未产生可验收的 `plots`、`manifest.jsonl`、`metrics.jsonl` 或 `summary.json`，因此 Phase C 不标记完成。v2 的 `RESERVED -> RUNNING -> FAILED` 历史及其失败日志/运行根保持原样，不重跑、不改写。

### 下一步与清理清单

- 用户可在 `group-pc` 本机 PowerShell 查看：

```powershell
$task='DDM4IP-BDD100K-SYNTH-Oracle-Pilot-v3'
$run='D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot-v3'
Get-ScheduledTask -TaskName $task | Get-ScheduledTaskInfo
Get-Content -Raw -LiteralPath "$run\status.json"
Get-Content -LiteralPath "$run\task.log" -Tail 50 -Wait
```

- `Ctrl+C` 只停止日志跟随，不停止 Scheduled Task。任务终态后，需要新的 SSH 只读验收交叉检查 `status.json`、完整 `status-history.jsonl`、`task.log`、`LastTaskResult`、16 个 prediction/kernel、manifest/metrics/summary SHA 链、尺寸/有限性和三项 Oracle 改善方向；在此之前不得报告 Phase C 完成或进入 Task 11。
- 新增/保留的项目专用证据路径：`D:\DDM4IP-runtime\temp\phaseC-kernel-hash-red-20260908`、`D:\DDM4IP-runtime\temp\phaseC-preflight-20260908-v5`、`D:\DDM4IP-runtime\experiments\phaseC-oracle-pilot-spec-20260908-v3.json`、`D:\DDM4IP-runtime\experiments\phaseC-oracle-pilot-launch-20260908-v3.log`、`D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot-v3`；未执行清理。



## 2026-09-08：Phase C CPU/CUDA physics device mismatch 修复与 Oracle pilot v4 启动（未完成）

### 完整启动核验与状态差异

- 已完整读取本机 `D:\Unsupervised Imaging Inverse Problems\WORKLOG.md`、远端 `WORKLOG.md`、总计划、known-blur design、known-blur implementation plan 和 canonical remediation plan。远端主机核验为 `DESKTOP-KBM1345`；远端仓库为 `D:\Unsupervised Imaging Inverse Problems`，分支为 `main`，只读状态为 `## main...origin/main`。既有脏工作树修改全部保留，未执行 git add/commit/push/pull/rebase/reset 或分支切换。
- 本机日志停留在 2026-09-07 Task 9；远端日志已有 2026-09-08 Phase C v1/v2/v3、kernel hash TDD 修复以及 v3 失败证据。因此本轮以远端较新的已验证事实为准，没有覆盖本机控制日志。

### TDD 根因、RED/GREEN 与最小生产修复

- 先在旧代码下运行新增回归 `tests\test_physics_device_mismatch.py`，得到 RED：`D:\DDM4IP-runtime\temp\phaseC-device-mismatch-red-20260908\red.log`，退出码 `1`，1 个测试 ERROR，SHA-256=`877D7BF3C319FC0BE0B59BA3BB15B19FF6BFF627AC572D1C71B6E8DDC70E8890`。错误与 v3 完全一致：`deepinv_loss.py:186` 的 DeepInv Blur `conv2d` 收到 CPU FloatTensor，而 physics filter 为 CUDA FloatTensor。
- 只读追踪确认：Oracle `Blur` 无 parameters，filter/buffer 和 `physics.device` 在 `cuda:0`；`run_model` 在 DPIR 输出后将 restored/prediction 和 corruption filter 保持在 CPU；旧 `reprojection_metrics` 只从 parameters 推断 device，空参数模型退回 CPU，故产生 mismatch。该结论由实际构造和复现 traceback 得到，未猜测性重构。
- 按 TDD 只修改 `ddm4ip\losses\deepinv_loss.py` 的 `reprojection_metrics`：优先读取 `physics.device`，无该属性时依次回退到 parameter、buffer、输入 device，再将重投影输入和观测移到 physics device；实验设计、指标定义和输出 schema 未改变。修复文件 SHA-256=`6BA878590F411ABFD008E4B9F44F67B4159348847004BA1A859EB633893F6502`。
- 新增测试文件 SHA-256=`590B7745A8ACD1D2F9E3E6C6059B8ECE0A66406AEDDA0BABE86F39513F1ACAB3`。修复后聚焦 GREEN 为 1/1、退出码 `0`；日志 `D:\DDM4IP-runtime\temp\phaseC-device-mismatch-green-20260908\green.log`，SHA-256=`44C1A936AE95FC1901E0AF73AF6A7784AD8DA3434D85A8830B46EA54F0A30F50`。

### 无训练门禁

- 完整 no-training unittest：`69/69`，退出码 `0`；日志 `D:\DDM4IP-runtime\temp\phaseC-device-full-20260908\unittest-full.log`，SHA-256=`72094551223BAE9C6F8D29E20E27FC351B5CA97F0062F3F2A9AB83DEE666AD36`。
- 四个 synthetic Hydra `--cfg job --resolve` 均退出码 `0`：`step1_bdd100k_synthetic.log` SHA-256=`7CF088C87DB5364359E53449708E3520B5076C4EBF72A45B53F13F268CB77616`，`step2_bdd100k_synthetic.log` SHA-256=`B0D970E9F95D479F392F53AFAE96B97669413EF56C82C427C064AF3BF93F90FA`，`step3_bdd100k_oracle.log` SHA-256=`E6112FD3B125415FEC9009C80170B380B1329977421FD9FBD7EE3C37068F0800`，`step3_bdd100k_synthetic.log` SHA-256=`1CC885320068D46C2001B45B5A1D9A96FFF92967B0A286EA4AB77F1AC5CC2A62`；目录为 `D:\DDM4IP-runtime\temp\phaseC-device-hydra-20260908`。
- 既有 AlexNet/DRUNet/DPIR 离线构造门重新通过：`HF_HUB_OFFLINE=1`、`TRANSFORMERS_OFFLINE=1`、network guard hits=`0`、退出码 `0`；结果 `D:\DDM4IP-runtime\temp\phaseC-device-offline-20260908\offline-result.json`，SHA-256=`81393E1A524C8C518B669574DC1976A6FE510814DC39414F1267939898E857C1`。既有 D 盘权重未下载、未替换。

### Oracle pilot v4 调度证据

- 创建全新 external spec `D:\DDM4IP-runtime\experiments\phaseC-oracle-pilot-spec-20260908-v4.json`，SHA-256=`5F4CF01E232041DB0CA1BBCCD3E5C65D3D842648E0736834D7C4F1FE23BE80C0`；仅使用已核验的 benchmark、`dev-reserve/pairs.jsonl` 和既有离线权重，固定 `stage=oracle`、`mode=pilot`、`variant=oracle`、`dataset.test.max_imgs=16`、`expected_manifest_records=16`。v1/v2/v3 spec、run root 和失败日志均未覆盖。
- 仅通过 `start_bdd100k_synthetic_task.ps1` 注册并启动新任务 `DDM4IP-BDD100K-SYNTH-Oracle-Pilot-v4`。launcher 退出码 `0`；日志 `D:\DDM4IP-runtime\experiments\phaseC-oracle-pilot-launch-20260908-v4.log`，SHA-256=`7B76EEE3C9FC5BA2FD9990BD2FB5E3F23797BB0CDC28DD13AFEB60723C7D2141`。reserved spec 已写入全新 run root `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot-v4`。
- 启动后只做一次存在性/更新快照：Scheduled Task 的 `LastTaskResult=267009 (0x41301，仍在运行)`；run root 存在，`environment.json`、`spec.json`、`status.json`、`status-history.jsonl` 和 `task.log` 均存在；快照时 `status=RESERVED`、history 只有 `RESERVED`、task.log 为 `reserved; execution has not started`，执行 PowerShell 进程存在。该快照不代表完成，之后没有在本轮持续轮询。

### 未解决风险与下一准入

- Phase C 仍未完成：v4 尚无终态和可验收 plots/manifest/metrics/summary。本轮不报告 PSNR/SSIM/LPIPS，不报告 16 个 prediction/kernel，不勾选 Phase C 完成条目。
- v1/v2/v3 的完整失败证据继续保留；其中 v3 的 `FAILED`、`LastTaskResult=1`、`RESERVED -> RUNNING -> FAILED`、task.log 及 0 plots 未修改。若 v4 出现与 CPU/CUDA physics mismatch 无关的新根因，应保留完整证据并停止扩展修改。
- 用户下一步可在 group-pc 本机查看 v4 的 `status.json`、完整 `status-history.jsonl` 和 `task.log`；终态后需在新的对话进行独立交叉验收（含 LastTaskResult、无重复触发、16 个唯一 source、16 个 prediction/kernel、完整 SHA 链、文件有限性/归一化和三项 Oracle 指标方向）。在该验收完成前不得进入 Task 11；即使 Phase C 完成，也不自动启动 Task 11。
- 本轮新增/保留清理清单：`D:\DDM4IP-runtime\temp\phaseC-device-mismatch-red-20260908`、`D:\DDM4IP-runtime\temp\phaseC-device-mismatch-green-20260908`、`D:\DDM4IP-runtime\temp\phaseC-device-full-20260908`、`D:\DDM4IP-runtime\temp\phaseC-device-hydra-20260908`、`D:\DDM4IP-runtime\temp\phaseC-device-offline-20260908`、`D:\DDM4IP-runtime\experiments\phaseC-oracle-pilot-spec-20260908-v4.json`、`D:\DDM4IP-runtime\experiments\phaseC-oracle-pilot-launch-20260908-v4.log`、`D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot-v4`；均为本项目专用证据，未执行清理。





## 2026-09-08：长期规则维护补记

- 已确认 DeepInv physics 的 device 解析规则不是一次性实验结果，而是未来 CPU/CUDA physics 调用的长期可复用约束；本机 AGENTS.md 已追加最小规则，更新后 SHA-256=118F3019CF6BF6B3B8AA3DABB6E03E433647B86177223D80CA69C4529939CFC6。
- 该规则未改变实验设计、数据划分、指标定义、输出 schema 或阶段授权；Phase C v4 仍等待终态和独立交叉验收。


## 2026-09-09：Phase D / Task 11 Step 1 b01 独立终态验收通过

### 授权范围与启动核验

- 本轮只授权 Task 11 Step 1 pilot 的 b01；未授权 b02、b04、b08、b16、b32、Step 1 full、Step 2、Step 3 或正式评估。v1–v5 的失败运行根继续保留。
- 按 AGENTS.md 完成新鲜启动核验：ssh group-pc hostname 为 DESKTOP-KBM1345；远端仓库为 D:\Unsupervised Imaging Inverse Problems，分支为 main，只读 git status 为 ## main...origin/main 加既有 AM/M/?? 修改；未执行 Git 写操作，也未覆盖用户修改。
- 远端 WORKLOG.md 的 v6 成功记录与 canonical remediation plan 的当前状态一致；本机控制日志仅作辅助上下文。

### b01 调度与配置

- 仅通过 D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1 创建并启动 Scheduled Task DDM4IP-BDD100K-SYNTH-Step1-Pilot-b01；launcher 退出码为 0，没有 direct 执行。
- external spec：D:\DDM4IP-runtime\experiments\phaseD-step1-pilot-spec-20260909-b01.json，SHA-256=A2040469FD2DDD9114CDEF841F94BB36DC8D93F8357BBFA500D254214FFEBC59；reserved spec.json SHA-256=153DAA0D2F2C2EA40B6E02350DDF4BD13E7AB64FA526BC4406EE2C0FFA86DF9E。
- run root：D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-pilot-b01；固定 batch_size=1、max_steps=512、loss.n_accum_steps=8。日志中的 Global batch size=8，因此这是 64 次 optimizer update 的短 pilot，不是 512 次 optimizer update。
- status.json SHA-256=E6422F31EA573E3E0AB9F14C2A2042333D62F361D39B90C494A123412260FF33；status-history.jsonl SHA-256=A9B06EA9E440676207881598B49056CD04FD6646253382723F1C3FE62ADE264F。

### b01 独立终态与交叉验收

- Scheduled Task 为 Ready，LastTaskResult=0，无 missed run；没有匹配 b01 的训练进程。终态严格为 RESERVED -> RUNNING -> SUCCESS，无重复终态记录。
- status.json 为 SUCCESS、exit_code=0；完整 task.log 为 8030 字节，SHA-256=8964F7AE9E54A8B0A989A6296A413AE6A18F7A1DD3950424C8DC49F78C65C0C9。日志包含真实 child command、Saved checkpoint、Saved network snapshot、Training finished at step 512 和 execution finished: status=SUCCESS exit_code=0。
- 终点 pair 均存在：training-state-512.pt（67264477 字节，SHA-256=425E0A3506EC00D5D8492356DCD41563EE951CBECA575DAF03937A532FF5CADB）与 network-snapshot-512.pkl（16862877 字节，SHA-256=D951CFFDEFA595F121BD97B52245282DC5121AA60CB2C24803612AF2CADBB88E）。内部 training-state 为 global_step=512，snapshot 为 global_step=513；两者均含 flow_nn。
- 远端固定 Python 只读加载 checkpoint：training-state 顶层键含 flow_nn/global_step/ema，全量 519 个张量有限；snapshot 的 flow_nn 为 RFNoPrecond，105 个 state keys 全有限。完整 task.log 未出现独立词边界的 NaN/Inf/Infinity/nonfinite。
- 终态 GPU 快照为 NVIDIA GeForce RTX 2070 SUPER，显存 469/8192 MiB、利用率 0%；训练进程已退出。该值是终态快照，不是运行期间峰值。

### 结果、风险与下一准入

- b01 已进入终态并通过当前可核验的执行/工件门；没有把单个子进程退出码 0 当作整体成功，而是同时核对了 scheduler、status、完整 history、完整日志、进程、GPU、文件 SHA 和 checkpoint 内部结构。
- 已知限制：由于 pilot 的 report_every_steps=16384 大于 max_steps=512，task.log 没有逐步数值 loss 曲线；本次以无 NaN/Inf 日志、终点全量张量有限和正常终点保存作为 loss 有限性证据，不能声称已经审计每一步的数值 loss 或运行期间峰值显存。后续 b02 前仍需在新授权下按同一门禁复核。
- 本轮停止，不启动 b02。下一准入是用户在新对话中明确授权下一个 Step 1 pilot，并继续使用全新 task/run root；Step 1 full 仍需 b32 通过后再次单独授权。

## 2026-09-08 Phase C Oracle pilot v4 独立终态核验（失败，Phase C 未完成）

- 在用户返回后通过新的 SSH 只读命令做了一次新鲜终态核验；没有重启任务，也没有持续轮询。远端主机仍为 DESKTOP-KBM1345。
- DDM4IP-BDD100K-SYNTH-Oracle-Pilot-v4 的 Scheduled Task 为 Ready，LastTaskResult=1，LastRunTime=2026-09-08 21:41:25 +08:00，未观察到 missed run。status.json 为 FAILED、exit_code=1，更新时间为 2026-09-08T13:56:14.811635+00:00。
- status-history.jsonl 由完整 JSON 对象解析后的状态严格为 RESERVED -> RUNNING -> FAILED，没有重复终态记录。v4 运行根和 environment.json、spec.json、status.json、status-history.jsonl、task.log 均存在；旧的 v1/v2/v3 运行根均仍存在，未覆盖或删除。
- v4 task.log 完整失败证据：D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot-v4\task.log，7387 字节，SHA-256=94E6835E2E8662C212BC9E45F56CC8E5A6D064F73475EE390C69246667747762。真实 traceback 为 ddm4ip\trainers\deepinv_denoiser.py:413 -> :384 调用 ddm4ip\utils\benchmark_metrics.py:204 时抛出 ValueError: complete source and paired-image metadata is required；这不是此前 CPU/CUDA physics device mismatch 的重复根因，而是新的 paired-image metadata 缺失问题。按授权边界保留证据并停止扩展修改。
- v4 的 plots 仅有 2 个文件：1 个 prediction-011ad6b2-1dfff443.png 和 1 个 kernel-011ad6b2-1dfff443.pt；没有 manifest.jsonl、metrics.jsonl 或 summary.json，因此不能验收 16 个唯一 source、16 个 prediction/kernel、完整 SHA 链、文件有限性/归一化或 PSNR/SSIM/LPIPS 三项 Oracle 方向。Phase C 不得标记完成。
- v4 关键文件核验：spec.json SHA-256=3D5C681DD8CC8398967089EEF460DF13BBF715D21002165C8802D34535BE16EF、status.json SHA-256=D60883F0E069D8B0F6F0A17C196F143612EF837D3BF8B8B31FC659DF2FA1F7C0、status-history.jsonl SHA-256=52FC9E3ED3CEB3301DF03C8AC90C53806BA025D081934924C98CCC9BE6BE64D3。
- 已完成的 device mismatch 修复、RED/GREEN、完整 no-training 69/69、四个 Hydra 解析和离线 AlexNet/DRUNet/DPIR 门禁仍有效；v1/v2/v3 失败证据完整保留。当前未授权修复新的 metadata 根因，也未启动任何训练、正式 500 图评估或 Task 11。
- 下一步边界：若要处理 v4 新的 metadata 根因，必须在新的对话中由用户单独授权“仅针对 paired-image metadata 的最小 TDD 修复与新 v5 Oracle pilot”；在该授权前不改代码、不重跑、不创建新任务。即使未来 v5 通过，也不自动进入 Task 11。
## 2026-09-09：Phase C paired-image metadata 链路修复与 v5 启动前门禁

### 完整启动核验与边界

- 已完整读取本机与远端 `WORKLOG.md`、known-blur design、implementation plan 和 canonical remediation plan；远端主机核验为 `DESKTOP-KBM1345`，实际仓库为 `D:\Unsupervised Imaging Inverse Problems`，分支为 `main`。本机日志停留在 Task 9，远端日志包含 Phase A/B、v1/v2/v3/v4，因此以远端较新状态为准，未覆盖本机控制日志。
- 启动时远端工作树已有修改均保留；未执行 git add/commit/push/pull/rebase/reset、分支切换或清理。v1/v2/v3/v4 的运行根、任务与失败证据均未修改。
- 本轮授权严格限于 Phase C 的 paired-image metadata 修复和新 v5 Oracle pilot；未进入 Task 11、训练或正式 500 图评估。

### 根因、RED/GREEN 与生产修复

- 独立重验 v4：任务为 Ready、`LastTaskResult=1`，`status=FAILED`、`exit_code=1`；history 严格为 `RESERVED -> RUNNING -> FAILED`。`task.log` SHA-256=`94E6835E2E8662C212BC9E45F56CC8E5A6D064F73475EE390C69246667747762`，真实错误仍为 `ValueError: complete source and paired-image metadata is required`，旧证据未覆盖。
- 只读链路追踪确认 `pairs.jsonl` 的 `source_sha256` 完整，`ManifestPairedDataset` 也在读取前校验该字段，但旧 `__getitem__` 构造 `Batch.meta` 时漏传它；`Batch.collate_fn`、device move 和 writer 本身均能保留/读取该字段。因此丢失点唯一定位在 manifest row 到 dataset metadata 的映射。
- 先扩展 `tests\test_manifest_paired_dataset.py`，在旧生产代码下得到精确 RED：`KeyError: 'source_sha256'`，日志 `D:\DDM4IP-runtime\temp\phaseC-metadata-red-20260909\red.log`，SHA-256=`EBED9672D2DD1C8DD4E744092ED03959D97FE265D2C5ECC035AFBACBE06C5B63`。
- 生产修复仅在 `ddm4ip\data\manifest_paired_dataset.py` 的 meta 映射中加入已验证的 `source_sha256`，未改变实验设计、数据划分、退化、指标、输出 schema 或路径合同。生产文件 SHA-256=`146AAF87DFE480E23A418E93F1AD104E7D58C802723A11D81B401260C8F03820`；测试文件 SHA-256=`092A0B7C42F13BBE5FDC07F6EF58C91FBD9B2C532B90B1EEC2001FCA7289ECFE`。
- 同一目标测试 GREEN 1/1、退出码 `0`；日志 `D:\DDM4IP-runtime\temp\phaseC-metadata-green-20260909\green.log`，SHA-256=`5DD985646FBDA5FD051A368264CA4A30AB2DA078888C9C24D38FFE66AF0B7633`。真实 dev-reserve 首样本经 dataset -> collate -> device move 后六个 writer provenance 字段均完整，退出码 `0`；日志 SHA-256=`79B0125DFAFB2C8C72A4BEA98C2F6EB9DAC8C995DD960346C50BF4C791F1E37B`。

### v5 启动前无训练门禁

- metadata/dataset/trainer/metrics/runner 聚焦回归 `35/35`、退出码 `0`；日志 `D:\DDM4IP-runtime\temp\phaseC-metadata-focused-20260909\focused.log`，SHA-256=`79EB447BCB061F74F6FD890EFD1FE2A94EF1BE13B60E1242490C1C563F80D0BA`。
- 完整 no-training unittest `69/69`、退出码 `0`；日志 `D:\DDM4IP-runtime\temp\phaseC-v5-full-unittest-20260909\unittest.log`，SHA-256=`4690CAF6ECA91A99466D870216E2E644AC6725B78B0B82EA2A8862132FBA1974`。
- 四个 synthetic Hydra `--cfg job --resolve` 均退出码 `0`；目录 `D:\DDM4IP-runtime\temp\phaseC-v5-hydra-20260909`。四份日志 SHA-256 依次为：Step 1 `7CF088C87DB5364359E53449708E3520B5076C4EBF72A45B53F13F268CB77616`、Step 2 `B0D970E9F95D479F392F53AFAE96B97669413EF56C82C427C064AF3BF93F90FA`、Oracle `E6112FD3B125415FEC9009C80170B380B1329977421FD9FBD7EE3C37068F0800`、learned Step 3 `1CC885320068D46C2001B45B5A1D9A96FFF92967B0A286EA4AB77F1AC5CC2A62`。
- AlexNet/DRUNet/DPIR 在 `HF_HUB_OFFLINE=1`、`TRANSFORMERS_OFFLINE=1` 和网络调用守卫下实际构造通过，退出码 `0`、network guard hits=`0`，设备均为 CPU。AlexNet 为 244408911 字节、SHA-256=`7be5be791159472b1fbf3c69796f7cb30dca7ad8466c2df70058c37116cdee02`；DRUNet 为 130585443 字节、SHA-256=`20296845d272d3d786b89ea3c1208d5f2ceb57658a499d4dd28073cbb73508aa`。成功证据目录 `D:\DDM4IP-runtime\temp\phaseC-v5-offline-20260909-v2`，log SHA-256=`657BCB9FCCD2B6038BB834DA8C28DA0B028D3673E3DFCED9C6DF692C06F0A50F`，result SHA-256=`79124974AB90BDAD8DFD9C95ED2641E17A57EED04AF3D3055D4385D1F160265F`。
- 首个离线审计脚本在三者已经构造后因错误地假定 DPIR wrapper 自身有 parameter 而触发 `StopIteration`；该证据保留在 `D:\DDM4IP-runtime\temp\phaseC-v5-offline-20260909`，log SHA-256=`64A1EB465778865979BF4722BE12CA5BC6C276273273AEA1CD54F5DC422E673E`。这只是临时记录器的设备取值错误，不是项目代码、metadata 链路或 Oracle 的新根因；v2 记录器按 parameter -> buffer -> 注入 DRUNet 回退后通过，未覆盖失败日志。

### 当前准入状态与清理清单

- paired metadata 根因已修复，用户要求的全部 v5 启动前门禁已通过；下一步仅允许创建全新 v5 external spec、任务和运行根并通过 Windows Scheduled Task 启动一次。v5 尚未启动，Phase C 尚未完成。
- 本轮新增并保留的项目专用证据目录：`D:\DDM4IP-runtime\temp\phaseC-metadata-red-20260909`、`phaseC-metadata-green-20260909`、`phaseC-metadata-focused-20260909`、`phaseC-metadata-diagnosis-postfix-20260909`、`phaseC-v5-full-unittest-20260909`、`phaseC-v5-hydra-20260909`、`phaseC-v5-offline-20260909` 和 `phaseC-v5-offline-20260909-v2`。均未清理；不得递归删除。

## 2026-09-09：Oracle pilot v5 独立终态失败（停止扩展）

- 新 external spec 为 `D:\DDM4IP-runtime\experiments\phaseC-oracle-pilot-spec-20260909-v5.json`，SHA-256=`A33DB192DC762DA149D62EE8264EA76E749C436ABAB8BAD23DE5B02ABA812AC2`；仅将 v4 的 task/run root 改为 v5，其余 Oracle、dev-reserve、16 图、benchmark hash 和 runner 合同保持不变。创建前确认同名 task、run root 和 spec 均不存在。
- 只通过 `D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1` 注册并启动 `DDM4IP-BDD100K-SYNTH-Oracle-Pilot-v5`；未 direct 执行。launcher 退出码 `0`，日志 `D:\DDM4IP-runtime\experiments\phaseC-oracle-pilot-launch-20260909-v5.log`，SHA-256=`7B76EEE3C9FC5BA2FD9990BD2FB5E3F23797BB0CDC28DD13AFEB60723C7D2141`。
- 启动后严格只做一次任务/进程/status/history/task.log/run root 快照。快照时任务已为终态：Task `Ready`、`LastTaskResult=1`、`LastRunTime=2026-09-09T09:04:33+08:00`，匹配 v5 的进程数为 `0`；run root 及 `environment.json`、`spec.json`、`status.json`、`status-history.jsonl`、`task.log` 全部存在。
- `status.json` 为 `FAILED`、`exit_code=1`，SHA-256=`ACF74826A7B48F9E83996953336059D4A626D8CE810CDFB128245B5043B9E998`；history 从完整对象读取后严格为 `RESERVED -> RUNNING -> FAILED`，无重复触发，SHA-256=`197A3175E9BCD57A36903C56B6185184CF0E5546047338C12120EABC6E61FB62`。reserved `spec.json` SHA-256=`01D97B4CD9A360762A7E093077878481920A3A14978622A7D865E56EEFDCA58C`，`environment.json` SHA-256=`9A6DD35B20D5920262F89B38B88AE8FA9BEEB1A5E8D4CB70009D7BAF61B4E077`。
- 完整失败日志位于 `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-oracle-pilot-v5\task.log`，9762 字节，SHA-256=`76FD74054948265F1ACC7EB384D166150D54375EBFBAA4C8F94EF4AF5EE94A1B`。paired-image metadata 的 `ValueError` 未再出现；新 traceback 在 DeepInv DPIR 初始化迭代的 `physics.A_adjoint(y)`，最终于 `conv_transpose2d` 抛出 `RuntimeError: cannot reshape tensor of 0 elements into shape [3, -1, 0, 0]`，说明传入的 physics filter 空间尺寸为 `0 x 0`。
- 该 filter 几何问题与本轮授权的 paired-image metadata 链无关。依用户边界，已保留 v5 完整失败证据并停止猜测性扩展：未调查或修改该新根因、未创建 v6、未重启任务、未运行训练、未运行正式 500 图评估，也未进入 Task 11。
- 因 v5 失败，Phase C 仍未完成；没有宣称 16 份 prediction/kernel、manifest/metrics/summary、SHA 链或 PSNR/SSIM/LPIPS 方向通过。下一阶段若要继续，必须在新对话中单独授权针对 `0 x 0` physics filter 数据链的诊断与新 pilot；Task 11 门禁继续关闭。
- v1/v2/v3/v4 与新增 v5 的 task、spec、run root、status/history/task.log 均保留且未覆盖。本轮新增清理清单包括 `D:\DDM4IP-runtime\experiments\phaseC-oracle-pilot-spec-20260909-v5.json`、`phaseC-oracle-pilot-launch-20260909-v5.log` 和 `bdd100k-synthetic-motionblur-v1-oracle-pilot-v5`；不得递归删除。

## 2026-09-09：Phase D / Task 11 Step 1 b02 已创建并托管，尚未终态验收

### 授权范围与启动核验

- 本轮只授权 Task 11 Step 1 的 b02 pilot；未启动 b04、b08、b16、b32、Step 1 full、Step 2、Step 3 或正式评估。b01 及其他历史 run root、任务和失败证据均未覆盖。
- 按 `AGENTS.md` 完成完整启动核验：本机 `WORKLOG.md` 与远端日志 SHA-256 不同，远端 `WORKLOG.md` 为最新事实源；`ssh group-pc` 主机为 `DESKTOP-KBM1345`；远端仓库为 `D:\Unsupervised Imaging Inverse Problems`、分支为 `main`；既有 dirty worktree 和未跟踪文件全部保留，未执行 Git 写操作。
- 启动前确认 b02 external spec、task 和 run root 均不存在；已存在的 b01 未复用或覆盖。

### b02 规格与调度证据

- external spec：`D:\DDM4IP-runtime\experiments\phaseD-step1-pilot-spec-20260909-b02.json`，SHA-256=`A4E416DBF25E2D71CB8AEB72F0E4BA8A21BABF5AD82BB01F903EDBEB2C79E094`。
- run root：`D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-pilot-b02`；Scheduled Task：`DDM4IP-BDD100K-SYNTH-Step1-Pilot-b02`。
- 固定 overrides：`training.batch_size=2`、`training.max_steps=1024`、`loss.n_accum_steps=8`；对应 global batch size 为 `16`，但本条不把 `max_steps` 解释为 optimizer update 数。
- 仅通过 `D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1` 注册并启动，launcher 退出码为 `0`；没有 direct 执行 runner 或训练。启动日志路径为 `D:\DDM4IP-runtime\experiments\phaseD-step1-pilot-launch-20260909-b02.log`。

### 启动后一次性存在性核验与边界

- 启动后的初次快照观察到 task 存在且为 `Running`、`LastTaskResult=267009 (0x41301)`，匹配 b02 的进程数为 `3`；run root、`status.json`、`status-history.jsonl` 和 `task.log` 均存在。
- 随后的单次干净存在性快照观察到 task 仍存在、状态为 `Ready`、匹配进程数为 `0`，run root、`status.json`、`status-history.jsonl` 和 `task.log` 仍存在。按用户边界，本轮没有读取这些文件内容、没有判断 SUCCESS/FAILED、没有持续轮询、没有重启或创建其他任务；因此 b02 只记录为“已启动，终态待后续独立核验”。

### 下一准入

- 本轮到此停止等待。下一步只能在用户新对话中明确授权后，对 b02 做一次独立终态验收（含 status/history/task.log、LastTaskResult、无重复触发、进程、有限性和终点 checkpoint pair）；在该验收完成前不得启动 b04，也不得进入 Step 1 full、Step 2、Step 3 或正式评估。

## 2026-09-09：Task 11 Step 1 b02 独立终态验收通过

### b02 终态交叉核验

- 本次只读独立核验未启动、重启或创建任何任务；远端主机仍为 DESKTOP-KBM1345，b02 Scheduled Task 为 Ready，LastTaskResult=0，NumberOfMissedRuns=0，最后运行时间为 2026-09-09T16:06:25+08:00，匹配 b02 的进程数为 0。
- b02 run root D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-pilot-b02、environment.json、reserved spec.json、status.json、status-history.jsonl 和 task.log 均存在。external spec 和 reserved spec 的 overrides 一致：training.batch_size=2、training.max_steps=1024、loss.n_accum_steps=8；global batch size 为 16，对应 64 次 optimizer updates。
- external spec SHA-256=A4E416DBF25E2D71CB8AEB72F0E4BA8A21BABF5AD82BB01F903EDBEB2C79E094；reserved spec.json SHA-256=01F78CC5C1BF16EFB9476554B4249AB846CBBEA87C079F7821A5865A8954FD4B；environment.json SHA-256=9A6DD35B20D5920262F89B38B88AE8FA9BEEB1A5E8D4CB70009D7BAF61B4E077。
- status.json 为 SUCCESS、exit_code=0，文件 457 字节，SHA-256=B684750448CCFF702F473601DAC41084E19E328AF72EBA150A2C0C6B68FEC8FD。完整 status-history.jsonl 按 JSON 对象边界解析为严格 RESERVED -> RUNNING -> SUCCESS，共 3 个对象、1 个终态对象，文件 953 字节，SHA-256=FFB982E1E2003F6047851F5D7BED14720B4380C0B83842D6EE85D7F39E18AC97，无重复终态。
- 完整 task.log 已读取，8037 字节，SHA-256=3589F0F59EBBEA0B87C1854AFA426D5C5F6496F1FEF2ACCCF0FBEA761BC96734；包含一次 Saved checkpoint、一次 Saved network snapshot、一次 Training finished at step 1024 和一次 execution finished: status=SUCCESS exit_code=0，没有 NaN/Inf/Infinity/nonfinite 独立词边界标记。
- 终点 pair 均存在于 checkpoints：training-state-1024.pt 为 67265000 字节、SHA-256=7990B8B09D7511EA1DA5D045BD006A3901F66FC225BB16533BF9656D8C412DC7，只读加载后内部 global_step=1024，顶层含 flow_nn，全量 519 个张量有限；network-snapshot-1024.pkl 为 16862877 字节、SHA-256=F4BD0DF7E62BE9B1BBAA67E7706D3E1D2E6E1AC08AAA654B9AE84E347953A811，内部 global_step=1025，含 flow_nn=RFNoPrecond，105 个模型张量有限。pickle 加载临时加入仓库根到 sys.path 后已恢复原路径，独立复核为 True。
- 与 b01 相同，pilot 的逐步 report 间隔高于本次短预算；本次不把单个日志退出码当作全部证据，而以 scheduler、状态历史、完整日志、无非有限标记、终点 checkpoint pair、内部 N/N+1 和全量张量有限性共同作为成功依据。

### 结论与下一准入

- b02 已完成本阶段允许的独立验收；b01、b02 均保留为独立成功证据。b04、b08、b16、b32、Step 1 full、Step 2、Step 3 和正式评估本轮均未启动。
- 下一步只能在新对话由用户单独明确授权 Task 11 Step 1 的 b04 pilot；必须创建全新的 task、external spec 和 run root，固定 (batch_size,max_steps,n_accum_steps)=(4,2048,8)，仍只通过 Scheduled Task 启动。b08、b16、b32 必须按顺序逐个新对话授权；b32 通过并完成独立终态验收后，Step 1 full 仍需再次单独授权。

## 2026-09-09：b02 之后的日志与规则同步

- 本次仅同步文档与长期规则，未创建、启动、重启或修改任何 Scheduled Task、run root、checkpoint、代码或数据；远端事实源仍为 DESKTOP-KBM1345 上的 D:\Unsupervised Imaging Inverse Problems。
- b02 的独立终态证据已在本日志上一节记录并保留：SUCCESS、完整 history、task.log、checkpoint pair 和内部 1024/1025 验收均通过；下一准入仍是新对话中用户明确授权的 b04 pilot，固定 batch_size=4、max_steps=2048、n_accum_steps=8。b08、b16、b32 必须按顺序单独授权和验收，b32 通过前不得进入 Step 1 full。
- 本机 AGENTS.md 已新增一条可复用规则：任何 Task 11 Step 1 pilot 的终态必须独立交叉核对 scheduler、进程、status、对象边界 history、完整日志、checkpoint SHA、内部 N/N+1、flow_nn 和全量张量有限性；SUCCESS 或单个退出码不能替代整组验收。更新后 SHA-256=B0B24BD1E1586E44D658D3AC1293A4A80EA8617E89539E324349380BEAAB75BC。
- 远端 Git 状态保持原样：仅做文档回写和只读核验，未执行 add、commit、push、pull、rebase、reset 或分支切换；旧失败运行根、b01/b02 证据和其他用户修改均保留。
- 本条记录只更新交接事实和规则，不把任何后续 pilot、full training、Step 2、Step 3 或正式评估视为已授权。

## 2026-09-10: Task 11 Step 1 b32 pilot slow-run and observability note (terminal acceptance pending)

- User reports b32 is markedly slower than the earlier b16 pilot. A fresh snapshot at 2026-09-10 13:27:10 +08:00 on DESKTOP-KBM1345 found the Scheduled Task Running, LastTaskResult=267009 (0x41301), status.json=RUNNING, and training PID 9060 responding.
- The same snapshot found GPU utilization=100% and VRAM=7757/8192 MiB (about 94.7%); the process started at 12:00:09 and was still computing. This supports active high-memory-pressure execution, not SUCCESS or FAILED.
- status.json had not advanced beyond 12:00:09 and task.log had last written around 12:00:15 while remaining in use; no per-update or per-epoch progress was visible. Treat throughput and observability as risks for later formal training.
- Before any later formal training (separate user authorization required), check VRAM headroom, optimizer-update time, total runtime, OOM/degradation risk, and append-only step/update progress logging. Do not assume a larger batch is faster. b32 still requires the full independent terminal acceptance and must not gate Step 1 full yet.


## 2026-09-10: b32 versus b16 runtime anomaly diagnosis (b32 still running)

- Fresh comparison: b16 used batch_size=16, max_steps=8192, n_accum_steps=8 and completed in about 8 minutes 28 seconds (reserved 09:42:45 +08:00, terminal status 09:51:13 +08:00), which is 64 optimizer updates under the configured global-batch accounting. b32 uses batch_size=32, max_steps=16384, n_accum_steps=8, also 64 optimizer updates, but was still Running at 14:56:47 +08:00 after about 177 minutes.
- b32 diagnostic evidence: main PID 9060 plus four live Python DataLoader workers; GPU utilization 99%, VRAM 7740/8192 MiB, temperature 77 C, power 105.77 W. This indicates active high-memory computation; it is not evidence of a scheduler failure or a clean terminal state.
- The b32 config has report_every_steps=16384 and save_every_steps=2097152. Therefore no intermediate report/checkpoint is expected before the final step; this explains the silent log, but does not explain the roughly 20x wall-time difference. Checkpoint directory was still empty at the diagnostic snapshot.
- Root cause is not yet fully isolated. Keep b32 unaccepted and do not enter Step 1 full; after termination, independently inspect final artifacts and perform a dedicated batch-32 throughput/memory diagnosis before any later formal training authorization.

## 2026-09-10: fresh read-only systematic diagnosis of b32 slowness

- Startup verification was repeated: the local control host is `zzz`; SSH `group-pc` reported `DESKTOP-KBM1345`. The remote repository was inspected without changing its existing dirty worktree. The remote `WORKLOG.md` was hash-checked before this append; no experiment source, configuration, benchmark, checkpoint, or task state was changed.
- At 2026-09-10 15:17:19 +08:00, `DDM4IP-BDD100K-SYNTH-Step1-Pilot-b32` was still `Running` with `LastTaskResult=267009 (0x41301)`. `status.json` remained `RUNNING`, and `status-history.jsonl` contained only `RESERVED` and `RUNNING` objects. The b32 task log contained only reservation/startup, the child command, and two startup warnings; no traceback, NaN, OOM, or progress line was present. `main.log` was empty.
- The b32 run root had the Hydra files, command/environment metadata, and an 88-byte TensorBoard event file, but no scalar/event records, plots, or checkpoint-like files. The task log was readable while the task remained active, but its active-file lock was not treated as terminal evidence. This is not a SUCCESS/FAILED acceptance.
- At 15:18:02, PID 9060 had four live direct Python DataLoader children. GPU 0 reported 100% utilization, 7773/8192 MiB VRAM, 77 C, and 105.57 W. At 15:25:22, current clocks were 1875 MHz SM and 6801 MHz memory; `nvidia-smi` showed no active thermal, power-cap, or hardware slowdown brake. At 15:24:54, the main process had accumulated about 2161 CPU seconds since 12:00:09, while the four workers had only about 28-31 seconds each; the sampled process I/O rates were zero and D: still had about 91.3 GB free. These observations support active GPU computation and do not support a continuously CPU/worker-bound or disk-full explanation, while leaving intermittent stalls unproven.
- The b16 and b32 resolved Hydra configurations are the same in the training/model/data paths except for the intended batch, max-step, and experiment-name overrides. With one world rank and `n_accum_steps=8`, b16 has `global_batch_size=128`, b32 has `global_batch_size=256`; both budgets are 64 optimizer updates and 512 train mini-batches in total. The b32 budget processes twice as many samples as b16, so a modest increase is expected, but the observed wall-clock lower bound (about 205 minutes by the 15:25 snapshot versus 8 minutes 28 seconds for b16) is about 24x; actual per-update progress remains unknown because no progress counter was emitted.
- `report_every_steps=16384`, `plot_every_steps=131072`, and `save_every_steps=2097152` mean that neither pilot should emit an intermediate report or checkpoint before its terminal forced save. The no-progress log is therefore partly an observability problem, not an explanation for the runtime. Python output is redirected to `task.log` without explicit flush, and the runner writes terminal status only after the child process returns.
- Code inspection found the expected accumulation loop: eight `FlowMatchingLoss` calls per optimizer update, followed by one `global_step += global_batch_size`. The data loader uses four persistent workers and pinned memory, but `Batch.to()` currently uses synchronous `.to()` transfers (`non_blocking=False`); uncached image reads and cache refill/GC are possible secondary costs. The low worker CPU time and 100% GPU utilization make those secondary hypotheses less likely than a batch-32 GPU performance/memory-pressure cliff, but the exact kernel or CUDA/cuDNN cause is not proven.
- Classification for this snapshot: (a) GPU compute under high VRAM pressure is the leading explanation, but not yet shown to be normal; (b) DataLoader/IO blocking is not supported by the fresh process/CPU/IO evidence, though intermittent waits are not excluded; (c) a first-round or CUDA-path failure is unconfirmed because the process has remained alive with active GPU work and no exception; (d) logging/heartbeat buffering is confirmed as an observability defect only; (e) synchronous transfer/cache overhead and a batch-32 algorithm-selection cliff remain unisolated alternatives. b32 remains unaccepted and no later stage is authorized.
- Before any later formal training, under separate authorization, add flushed update-level progress/heartbeat records, optimizer-update and data/compute timing, CUDA allocated/reserved/peak memory, GPU utilization/temperature/power/clock samples, DataLoader wait metrics, and a short controlled b16/b32 throughput gate. Until then, leave the current task untouched and perform no automatic restart or cleanup.

## 2026-09-10: b32 pilot terminal result and independent acceptance

- A new remote snapshot at 2026-09-10 15:55 +08:00 confirmed host `DESKTOP-KBM1345`, Scheduled Task `DDM4IP-BDD100K-SYNTH-Step1-Pilot-b32` in `Ready` state with `LastTaskResult=0`, no matching runner/training processes, and GPU idle. `status.json` reports `SUCCESS` and `exit_code=0`. The status history was parsed as three complete JSON objects: `RESERVED`, `RUNNING`, and `SUCCESS`.
- The full task log ended with `Training finished at step 16384` and `execution finished: status=SUCCESS exit_code=0`; its SHA-256 is `F66AAFA2D7145FFF6CDBF2F3D2F2B95FE5383E8D8D0B198169DDBF97DD113D21`.
- Independent checkpoint validation passed. `training-state-16384.pt` SHA-256 is `5D556C3A42C359C0E21AC37E47B5179215865425C3C819BDB1D314463B7573EA` and contains `global_step=16384`. `network-snapshot-16384.pkl` SHA-256 is `BC091949D381B3765B4A2A8221EA952AC183E675931CC1150EAB9FE4995376A2` and contains `global_step=16385`, matching the project checkpoint convention.
- The two endpoint `flow_nn` state dictionaries have exactly 105 identical keys. All checkpoint tensors scanned as finite; no non-finite tensor paths were found in the training state or the network snapshot. This independently accepts the b32 pilot as a successful terminal run, but does not itself authorize Step 1 full, Step 2, Step 3, or formal evaluation.

## 2026-09-10: Task 11 Step 1 formal b16 fallback decision

- After independent acceptance of the b32 pilot, the user selected b16 as the formal Step 1 fallback because b16 completed the same 64-update pilot in about 8 minutes 28 seconds while b32 required about 3 hours 53 minutes. The accepted b32 run root and checkpoint pair remain immutable scale/performance reference evidence.
- The parent Phase E full contract is `batch_size=32`, `n_accum_steps=8`, `max_steps=5242880`, `report_every_steps=16384`, `plot_every_steps=131072`, and `save_every_steps=2097152`. The b16 route keeps the approved dataset/model/loss/seed/evaluation boundaries but changes the formal batch to 16 and effective global batch to 128.
- The b16 formal budget is intentionally not inferred from the pilot. Before execution, the new spec must select either sample/global-step preserving (`max_steps=5242880`, 40960 optimizer updates) or optimizer-update preserving (`max_steps=2621440`, half the parent global-step/sample budget, explicitly reported as budget-reduced). `max_steps=8192` remains pilot-only. The sample-preserving option extrapolates to roughly 90 hours from the pilot rate, so schedule feasibility must be checked before launch.

## 2026-09-10  Task 11 Step 1 b16 formal fallback launch

- Per the approved b16 fallback amendment and Scheme A, launched exactly one new Step 1 formal training task through D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1.
- Frozen contract: batch_size=16, n_accum_steps=8, effective global batch 128, max_steps=5242880, expected optimizer updates 40960, report_every_steps=16384, plot_every_steps=131072, and save_every_steps=2097152. This is sample/global-step preserving; it is not numerically equivalent to b32 and is not a budget-reduced fallback.
- Fresh prelaunch audits passed: host DESKTOP-KBM1345; benchmark status SUCCESS, source count 1739, split counts 1000/100/500/139, paired files and pixels passed, kernel [1,1,32,32] finite and normalized; b16 and b32 pilot provenance passed with terminal .pt steps 8192/16384, .pkl steps 8193/16385, finite tensors, and exact RESERVED -> RUNNING -> SUCCESS histories.
- Current runner SHA-256: 9ED9344827D11A051AD60416A4E9F8085A9026D89105C15E48F76510CE4C8710. External spec: D:\DDM4IP-runtime\experiments\phaseE-step1-full-spec-20260910-b16.json, SHA-256 7EB34570517FC3D0384B473A94EE7430125ECB68511E573D85652EA2D3BB8471. New run root: D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-full-b16.
- Scheduled Task DDM4IP-BDD100K-SYNTH-Step1-Full-b16 launcher exit code was 0. One immediate post-dispatch snapshot showed Task Scheduler Running, LastTaskResult=267009 (0x41301), status.json=RUNNING, the new run root/spec/status/log present, and three matching launcher/runner/training processes. No Step 2, Step 3, evaluation, data processing, weight download, code change, or benchmark change was performed.
- Terminal checkpoint acceptance remains pending a separate fresh user-requested conversation; this entry records launch only, not formal training completion.
## 2026-09-17: GitHub source publication completed; no training restarted

- Scope explicitly confirmed by the owner: publish complete project source and documentation to https://github.com/saadxxx847-ai/Unsupervised-Imaging-Inverse-Problems.git; exclude datasets, pretrained weights, training checkpoints, caches, and experiment outputs. The target is a public repository owned by saadxxx847-ai.
- Full startup verification completed: local WORKLOG read in full, SSH host DESKTOP-KBM1345 verified, remote main worktree and index inspected and preserved, remote WORKLOG read in full. The approved 2026-09-06 design and 820-line implementation plan, plus the b16 fallback amendment and plan, were read in full. The remote log is newer than the local control log; neither history was overwritten to reconcile them.
- Source base: upstream inria-thoth/ddm4ip commit 7804d029aeb66ba6e2b20db00ff846ff3d6403cf. All five existing commits and MIT license were preserved. The 197 source working-tree files were frozen with byte SHA-256; eight existing runtime source files were copied into the publication's scripts/orchestration directory. This is a versioned preservation copy; active runtime scripts were not moved or modified.
- Publication was committed and pushed only from the owner's authenticated personal computer, using the isolated directory D:\Unsupervised Imaging Inverse Problems\github-publication-20260917\repository. No GitHub credential, Git commit, push, fetch/pull, branch change, or remote configuration change was made on group-pc. Remote Git index SHA-256 before/after snapshot: 2EE2DB58AFFB1845A516B7E2B86F09DBFF1FC4C27A81ED84AE7BFB8F888CC276.
- Initial source publication commit: 4ab521428fa0cc6de4a5a660f7a79df68b50045e. Commit/push commands exited 0. Independent GitHub API verification read refs/heads/main and the full recursive tree: all 209 file blob hashes matched the local commit, with no truncated response. git fsck --full exited 0. Pattern scans of staged source and all five upstream commits found no matching common credential/private-key patterns; this is a pattern check, not a guarantee against every possible secret. No data/model artifact extensions were present in the published tree or model-weight paths in history.
- The source archive repository.tar.gz is 2828624 bytes, SHA-256 664EDBCA4C63B3DC01C1C386881FDD1E439E816E1D17D398EC5DFEE9E9E7E1F8. Runtime source archive orchestration.tar.gz is 9103 bytes, SHA-256 0C8EDED4267795595E1612D7C94A44986DF257AFD76803DF7DE267E6A51C1654. Both archives and both manifest files matched after transfer. Original byte hashes are preserved in docs/publication; Git text newline conversion is documented in PUBLICATION.md.
- No project code behavior, training budget, dataset, checkpoint, task, or runtime script was changed. Project tests, training, inference, evaluation, and data processing were not run for publication. Publication checks verify transfer/Git integrity; prior test outcomes remain historical evidence only.
- The user reported a network interruption. A single fresh scheduler snapshot found DDM4IP-BDD100K-SYNTH-Step1-Full-b16 in Ready state with LastTaskResult=0. This does not independently establish complete formal training or validate its checkpoints. The existing run root D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-full-b16 remains untouched. No restart or downstream execution was authorized or performed.
- Documentation closure: this WORKLOG appendix and a matching canonical-plan appendix record the verified initial publication commit; a subsequent documentation-only commit will synchronize these records to GitHub. The final documentation commit can be checked from GitHub main without making any training acceptance claim.
- Cleanup inventory (project-exclusive, retained): remote D:\DDM4IP-runtime\transfer\github-source-publication-20260917 contains repository.tar.gz, orchestration.tar.gz, source-manifest.json, orchestration-manifest.json, and archive-files.txt; local D:\Unsupervised Imaging Inverse Problems\github-publication-20260917 contains the downloaded archives/manifests, remote-snapshot, isolated publication repository, documentation patches, and verification receipt. No environment or dependency installation was performed. Do not bulk-delete these paths; the publication repository is a useful personal Git working copy, while archives/snapshot are retained transfer evidence.
- Next admission: in a new conversation, explicitly authorize only read-only independent acceptance of the existing b16 formal run, checking scheduler/processes, status/history by complete JSON objects, full task.log, resolved configuration, endpoint training-state-5242880.pt and network-snapshot-5242880.pkl, SHA-256, internal 5242880/5242881, flow_nn keys, and all tensor finiteness. Do not restart based only on loss of network connectivity. Step 2, Step 3, formal evaluation, data processing, weight downloads, new tasks, and resumed training remain separately authorized stages.

## 2026-09-17: Step 1 full b16 checkpointed restart launched

- Scope explicitly confirmed by the owner: restart the interrupted synthetic BDD100K Step 1 full training and make it recoverable after a power interruption. No Step 2, Step 3, evaluation, data processing, weight download, or Git operation was authorized or performed.
- The just-started run D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-full-b16-restart-20260917 was stopped with Stop-ScheduledTask before any checkpoint existed. The independent stop snapshot showed three matching processes before and zero afterward; its run root, status, history, log, and claim evidence were retained. The older formal b16 run D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-full-b16 remains untouched.
- New external spec: D:\DDM4IP-runtime\experiments\phaseE-step1-full-spec-20260917-b16-checkpointed.json, SHA-256 890DB84EFF0158E3910A9437C4F213872EEBB5F68C90F05B029A45D9E5005F5A. New run root: D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-full-b16-cp-20260917.
- Frozen b16 Scheme A contract: batch_size=16, n_accum_steps=8, effective global batch 128, max_steps=5242880, report 16384, plot 131072, and save_every_steps=1048576. Expected checkpoint endpoints are training-state-1048576.pt, training-state-2097152.pt, training-state-3145728.pt, training-state-4194304.pt, and the forced terminal training-state-5242880.pt, with corresponding network snapshots. The current run had zero checkpoints at the launch snapshot; this list is the configured schedule, not completion evidence.
- New scheduled task DDM4IP-BDD100K-SYNTH-Step1-Full-b16-cp-20260917 was launched only through D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1; launcher exit code was 0. One immediate post-dispatch snapshot on DESKTOP-KBM1345 showed Task Scheduler Running, LastTaskResult=267009 (0x41301), status RUNNING, three matching processes, and an updated task.log. The immutable child command recorded training.save_every_steps=1048576.
- Recovery wrapper D:\DDM4IP-runtime\orchestration\step1_resume_watchdog.ps1 was uploaded as a project-exclusive runtime artifact; PowerShell parse passed and its SHA-256 is 2DBC7B738B9E77C669B07B088F98F5D763E5F9641CD472D3AA38FF97C2422141. An active-process dry-run passed and skipped duplicate invocation. After an interruption, it archives a stale execution.claim, then invokes the existing stage runner against the same reserved spec so BaseTrainer auto-loads the latest training-state-N.pt; if no checkpoint exists yet, recovery necessarily starts from step 0.
- Recovery task DDM4IP-BDD100K-SYNTH-Step1-Full-b16-cp-recovery-20260917 was registered for the current user's next logon. Independent scheduler export confirmed a LogonTrigger, StartWhenAvailable=true, MultipleInstances=IgnoreNew, and the task settings show RestartCount=3 and RestartInterval=PT5M. Both training and recovery tasks were updated to ExecutionTimeLimit=PT0S (no default 72-hour cutoff); the recovery task also allows battery operation and does not stop when power mode changes.
- User-side status commands: $task='DDM4IP-BDD100K-SYNTH-Step1-Full-b16-cp-20260917'; $run='D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-full-b16-cp-20260917'; Get-ScheduledTask -TaskName $task | Get-ScheduledTaskInfo; Get-Content -Raw -LiteralPath "$run\status.json"; Get-Content -LiteralPath "$run\task.log" -Tail 50 -Wait. Ctrl+C stops only log following, not the scheduled task.
- Cleanup inventory (project-exclusive, retained while active): D:\DDM4IP-runtime\orchestration\step1_resume_watchdog.ps1; D:\DDM4IP-runtime\experiments\phaseE-step1-full-spec-20260917-b16-checkpointed.json; D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-full-b16-cp-20260917; D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step1-full-b16-cp-recovery-20260917\recovery.log; local control copies D:\Unsupervised Imaging Inverse Problems\step1_resume_watchdog.ps1, D:\Unsupervised Imaging Inverse Problems\phaseE-step1-full-spec-20260917-b16-checkpointed.json, and D:\Unsupervised Imaging Inverse Problems\WORKLOG-remote-reconcile-20260917.md.
- Next gate: after the run reaches a terminal state, a new conversation must independently verify scheduler state, complete status/history JSON objects, full task log, resolved configuration, terminal checkpoint pair SHA-256, internal global steps 5242880/5242881, exact flow keys, and tensor finiteness before any Step 2 admission.


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

- 本轮严格按 `AGENTS.md` 完成启动核验：本机 `WORKLOG.md` 只作较旧辅助上下文；远端主机核验为 `DESKTOP-KBM1345`，启动核验阶段远端 Git 只执行只读 `status`，并完整读取远端最新 WORKLOG、2026-09-06 批准设计与实施计划、b16 fallback amendment/plan、canonical remediation plan、`NEXT_SESSION.md` 和 `audit-report.md`。所有既有未提交/暂存修改、baseline、旧报告、旧 manifest、旧 `candidate.patch` 和训练证据均保留。
- 本轮唯一训练新鲜状态快照于 2026-09-19 18:19 +08:00 完成：任务 `DDM4IP-BDD100K-SYNTH-Step1-Full-b16-async-20260918` 为 Running，`LastTaskResult=267009`，`status.json=RUNNING`；wrapper/runner PID 23936/22068 存在，`task.log` 正在更新，最近已保存 step 1327104 checkpoint pair。该快照只证明当时仍运行，不代表终态；之后未持续轮询、停止或重启训练。
- 修改前冻结：candidate 209 个文件，聚合 SHA-256=`42F265FB5AC25DB9571310A40F12E75591D4FCBA5894FC1821B609D86229B646`；清单 `evidence\session4-20260919\candidate-before.json` SHA-256=`AE92C12E732CE0DEB84B2E522C093AA51CA903834464353E5F5B850896BAE234`。修改后 candidate 210 个文件，聚合 SHA-256=`9F0A12A69CE6723EC6C3D0849F899FC48E2B91205A4BB3E4E70158DAD47606C5`，本轮新增/修改 15 个文件；after 清单 SHA-256=`F73B6B6389101808039C6DBA8F73041D603EEC3264F3A4B02E5275503BB8D4AF`。
- 已在 candidate 修复 synthetic 状态/launcher 故障闭环：history 追加并 fsync，`status.json` 经同目录临时文件、fsync、`os.replace` 原子发布；替换失败保留旧完整状态、追加历史和临时证据；终态禁止覆写。计划任务注册或启动失败调用 `dispatch-failed`，在 reserved run 的 log/history/status 中记录 `failure_phase=dispatch`；注册失败与启动失败均有无真实计划任务的 PowerShell mock 注入夹具。
- 已在 candidate 补齐 checkpoint pair 中断协议：新保存先发布 `checkpoint-pair-N.pending.json`，两份正式文件落地并计算 SHA-256 后再原子发布 `checkpoint-pair-N.json`，最后移除 pending。恢复遇到无 commit 的 pending 时拒绝回退；最高 commit 对应文件损坏时拒绝静默选择旧 checkpoint。历史双文件 checkpoint 在两份文件都存在时仍兼容加载。另修复训练循环丢弃 `maybe_validate()` 返回 iterator 的问题。
- 已在 candidate 建立 kernel/evaluation checkpoint 绑定：learned Step 3 的冻结 Step 2 snapshot SHA-256 由 spec 注入 evaluation，写入逐图记录和 summary；最终聚合同时核对 seed、真核 SHA 和 snapshot SHA，错误 checkpoint/seed/source 夹具均 fail closed。外部 orchestration 测试统一改由 `DDM4IP_TEST_ORCHESTRATION` 显式注入，不再按测试文件层级推断或默认读取 live 路径。
- RNG/数据游标只形成证据与方案，没有改变协议：CPU 夹具证明 `InfiniteSampler(start_idx=已消费样本数)` 可重建索引尾序列，但仅重设 seed 不能重建 Python/NumPy/Torch 随机流；恢复 RNG state 只在单进程夹具中成立。多 worker、persistent worker 和 prefetch 队列仍未捕获，现有 b16/历史 checkpoint 不能宣称严格随机流等价恢复。方案见 `resume-reproducibility-plan.md` SHA-256=`08AB79948A1462A33EDA5064383D093F8B37FAA566C18ECEE17632947A764E11`。
- 测试先行证据全部保留：初始 red 为 72 项、退出码 1（其中一个测试夹具 NameError 后续修正，不计作产品缺陷）；定向 green `green-targeted-2.log` 为 72/72、退出码 0；最终新鲜完整 CPU 验收 `final-all.log` 为 123 项运行、5 项既有 CUDA 条件跳过、0 fail、退出码 0，`IMPORT_ISOLATION_OK 80`。最终日志 SHA-256=`F7604988876E9E678A832D73BB39F86A3409DDB5279FE1F13810049FEB14EDCC`。全程 `CUDA_VISIBLE_DEVICES=-1`、网络被 harness 禁止，未安装依赖。
- 审查交付均位于 `D:\DDM4IP-runtime\code-audit\20260919-systematic\evidence\session4-20260919`：逐文件 before/after SHA 清单 `session4-file-sha256.json`=`A4AE63B1930E17781C7E1BCC19A353D8D1E3454B4FCDF726C60EF8B13CD4A4A5`；baseline 到当前 candidate 的累计补丁 `candidate-cumulative-after-session4.patch`=`8551165EC52E5C8ECEB5C1DBAEA26EEDEA3F24C138985C46740EB90060B9EC9D`（旧 `candidate.patch` 未覆盖）；测试汇总 `session4-test-results.json`=`063BB3590C829408F26C0E4F106B9AD11C84320844249466FFC569C25FAACFB2`；问题清单 JSON/CSV=`8EAE14C8FD3FA6CBFD5B92022E0610329B8D41BEC5340400A070D42B9CFB8086`/`DE36B1F8857CD1827734348B3DCBF1BA6897C085AED230375739C33D5B5B3CBE`；补充报告 `audit-addendum.md`=`677A3BA707F934AF1262BA5B7EFAD9FE963526F3FB176A24ECB724F5035D5CBA`。
- 保护复核：原保护清单中的 203 个 live/运行器文件仅有本轮开始前已知的 WORKLOG 和 canonical plan 两项文档哈希变化；其余 201 个 live 源码、配置和部署运行器仍与审查前原 SHA-256 一致。Git index SHA-256 仍为 `2EE2DB58AFFB1845A516B7E2B86F09DBFF1FC4C27A81ED84AE7BFB8F888CC276`。本轮结束时只更新本 WORKLOG 与 canonical plan；未执行 `git add/commit/push/pull/checkout/reset`、未改变 index/ref/worktree。需要如实记录一项边界偏差：结束核验时误调用了一次 `git write-tree`，该命令可能物化不可达 tree object；发现后未再执行 Git 写命令，也未尝试清理对象。索引文件哈希前后一致，上述 201 个文件复核无漂移。
- 未执行/未声称：没有部署 candidate，没有修改 live 源码/配置/运行器/共享缓存，没有 GPU 验证、真实计划任务、Step 2/3、正式评估或数据处理。checkpoint marker、状态写入和跨工件绑定目前只通过隔离 CPU/PowerShell 夹具；GPU、真实跨阶段加载与 live 部署仍须独立授权。
- 清理清单（本项目专用、保留）：远端 `D:\DDM4IP-runtime\code-audit\20260919-systematic` 新增 `session4_freeze.py`、`session4_finalize.py`、`evidence\session4-20260919` 及测试保留的 `temp` 夹具；本机新增 `D:\DDM4IP-local-runtime\code-audit-20260919\session4-working`、`session4_freeze.py` 和 `session4_finalize.py`。未安装包、未写公共缓存；不得递归批量删除。
- 下一准入保持不变：先由用户在新对话明确授权当前 Step 1 full 的只读独立终态验收；未验收前不部署。部署仍需另行授权，逐文件 CAS 比较 live 当前 SHA 与清单 before SHA，并处理 runner hash/spec 迁移；不一致即停止。RNG exact-resume 设计、GPU 回归、Step 2/3 和正式评估均是后续独立阶段。

## 2026-09-20：训练期间 NumPy RNG 隔离候选修复第 1 步完成（candidate-only，未部署）

- 本轮严格完成启动核验：本机 `WORKLOG.md` 380 行、SHA-256=`808D0CE06F7D86540FF11E6E0890D789DC4F285C931462910C7A5B64D5F4765E`，仅作为较旧辅助上下文；SSH 主机为 `DESKTOP-KBM1345`；远端 Git 只读 `status` 已核对并保留全部既有暂存/未提交修改；远端最新 WORKLOG 583 行、修改前 SHA-256=`35E273164E4A2C2D1798E118C49DAE38992D173CD09279B8DFA5D50FAF2D6533`，已完整读取。批准的 synthetic BDD100K 设计、原实施计划，以及既有 `audit-report.md`、`NEXT_SESSION.md`、Session 4 addendum、`resume-reproducibility-plan.md` 均完整读取。
- 对当前 Step 1 full 只做了一次新鲜状态/进程存在性核验，时间为 `2026-09-20T12:56:09.2750102+08:00`：任务 `DDM4IP-BDD100K-SYNTH-Step1-Full-b16-async-20260918` 为 Running，`LastTaskResult=267009`，status 为 RUNNING，wrapper/runner/train 三个匹配进程存在，`task.log` 当时仍在更新。此后没有再次轮询、停止或重启训练。
- 新建独占审计根 `D:\DDM4IP-runtime\code-audit\20260920-numpy-rng-isolation`。Session 4 历史记录为 210 文件、总 SHA-256=`9F0A12A69CE6723EC6C3D0849F899FC48E2B91205A4BB3E4E70158DAD47606C5`；本轮冻结时源 candidate 实际为 217 文件、总 SHA-256=`C0BA203D6A8D8A7CFD0270A7EC48CD0849470B9EA96E28E3EF65A368D81D9ABC`，差异仅为 7 个 `__pycache__/*.pyc`。未删除或改写这些残留；旧 210 文件 manifest 与新鲜 217 文件 manifest 均保留，baseline/工作副本在修改前逐文件复核一致。
- 严格测试先行：新增 3 项回归。RED 运行 3 项、退出码 1，只有“调用后 NumPy 全局随机序列不变”按预期失败；“同一 `rnd_seed` 位级相同”和“官方 32×32 核有限、非负、和为 1”已通过。最小实现仅修改隔离副本 `ddm4ip\degradations\blur.py`：调用前 `get_state()`，保留原 `seed` 和核算法，在 `finally` 中 `set_state()` 恢复。目标 GREEN 为 3/3、退出码 0。
- 核不变门禁通过：冻结 benchmark `D:\DDM4IP-runtime\synthetic-benchmarks\bdd100k-motionblur-v1\degradation\kernel-gt.pt` 从未改写，文件 SHA-256 始终为 `4E292CA42C026965EF9B6D16CACEC83091DFC2E461C2C6788C6FDC690F832A7A`；修复前后生成 tensor 与冻结文件中加载出的 tensor 逐字节相等，tensor SHA-256 均为 `C9B12867CE2B271084B1A48CF871BD0585ADDF23C7FEC2D755F0D136F6495C11`。一次把重新序列化 `.pt` 容器 SHA 当门禁的尝试因 legacy `torch.save` 容器字节不稳定而 wrapper 退出 1，但 Python 生成本身退出 0 且 tensor SHA 已匹配；该尝试原样保留，正式门禁使用 tensor 原始字节并同时只读固定原文件 SHA。
- 完整 CPU 审计命令为 `E:\Anaconda3\envs\ddm4ip\python.exe D:\DDM4IP-runtime\code-audit\20260920-numpy-rng-isolation\run_cpu_audit.py ALL`：126 项运行、5 项既有 CUDA 条件跳过、0 fail、退出码 0，`IMPORT_ISOLATION_OK 81`；日志 SHA-256=`1A359B51982BA5A1A30A18518EE729E3D9DD4910BC1CB5468C16C854DAA12E12`。harness 显式设置 `CUDA_VISIBLE_DEVICES=-1`、阻断 socket 连接，并设置 HF/Transformers 离线；没有使用 GPU、网络下载或新依赖。
- 最终 candidate 218 文件，总 SHA-256=`1F506D242FB3CB504610308703A985634DC60CAD34D95C1C36175CFFE5F97BD4`。相对 217 文件 baseline 恰好两个变化：`repository/ddm4ip/degradations/blur.py` 从 `D068F0B95F8D37822C8337446B881C9997445B833FD7D51E99EB46AF98C769CD` 变为 `A3CEF4FC32DE3C3ADE406C6FBDCAFAFB9E080574EE8D0A3F767E8C2AAE45CB05`；新增 `repository/tests/test_motion_blur_rng.py`，SHA-256=`00B0A2CADD361837590C5A8DC2A3629F6C53CB62605B733667193083C868566A`。
- 审计入口：`audit-report.md` SHA-256=`D026F7BF9D80727CC2FFCFCAC3D1EF60810EB8E189280AF75828B0D245FFB4EC`；`evidence-index.json` SHA-256=`071AC69AD992FD14FFF16C85212FF9C2E5AB12173985439FC247520B1F61E739`；`NEXT_SESSION.md` SHA-256=`74541FB8FC5D9533BA1C6CA51C7B404C11FA6FC23B11234E8C123FBEC1FE7164`。逐文件 baseline/after 清单、两文件 diff、RED/GREEN/full 日志、核前后 JSON、测试汇总和命令账本均由 index 冻结。
- 未执行/未声称：没有修改 live 源码、配置或外部 runner，没有写共享缓存、当前训练运行根、reserved spec、状态、日志或检查点；没有部署、GPU 验收、新计划任务、精确恢复实现或 Step 2。本次唯一 live 仓库写入为按规则追加本 WORKLOG。
- 清理清单（本项目专用、保留）：远端 `D:\DDM4IP-runtime\code-audit\20260920-numpy-rng-isolation`（baseline、candidate、evidence、独立 cache/temp/pycache、报告与辅助脚本）；本机 `D:\DDM4IP-local-runtime\rng-session-20260920`（上传前副本和最终报告副本）。未安装环境或包，不得递归批量删除。
- 下一准入仅为新对话中的 candidate 独立只读验收：复核 218 文件总 SHA、仅两项变更、RED/GREEN/full CPU 日志和核 SHA 门禁，并判断是否满足“可另行申请 live 部署评审”。该验收不得修改 candidate 或 live；live 部署、GPU 验收、精确恢复和 Step 2 仍需之后分别明确授权。
## 2026-09-20：NumPy RNG 隔离 candidate 独立只读验收——代码证据通过，补丁工件阻塞部署评审准入

### 启动核验、授权边界与训练快照

- 本轮按 `AGENTS.md` 完成完整启动核验：本机 `WORKLOG.md` 为 380 行、SHA-256=`808D0CE06F7D86540FF11E6E0890D789DC4F285C931462910C7A5B64D5F4765E`，仅作较旧辅助上下文；SSH 主机核验为 `DESKTOP-KBM1345`；远端仓库 `D:\Unsupervised Imaging Inverse Problems` 的既有 `AM/M/??` 修改全部保留；远端最新 `WORKLOG.md` 为 1,186 行、修改前 SHA-256=`53CB0D967224FDB1B66E7C9DE10A213E340935E84DD8C8A3E6E77744B38F134D`，已完整读取。远端日志明显新于本机日志，本轮以远端为事实源，没有覆盖本机日志。
- 本轮只授权 `D:\DDM4IP-runtime\code-audit\20260920-numpy-rng-isolation` 的 candidate 独立只读验收。没有修改 live 源码、配置、runner、candidate、baseline、既有 evidence、benchmark、训练运行根、reserved spec、状态、日志或 checkpoint；没有部署、使用 GPU、启动计划任务、实现精确恢复或进入 Step 2。
- 对 Step 1 full 只执行了一次新鲜存在性快照，时间为 `2026-09-20T17:53:29.9242602+08:00`：`DDM4IP-BDD100K-SYNTH-Step1-Full-b16-async-20260918` 为 `Running`，`LastTaskResult=267009 (0x41301)`，状态文件存在，按 task/run-root 精确命令行过滤有 2 个匹配的 wrapper/runner 进程。该快照不构成终态或训练完整性判断；此后没有再次轮询、停止或重启。

### 指定工件与 candidate 清单独立复核

- 已完整复核用户指定的 `audit-report.md`、`evidence\candidate-after.json`、`candidate-changes.json`、`candidate.patch`、`test-results.json`、`kernel-before-v2.json`、`kernel-after.json` 和 `evidence-index.json`。八个文件从远端二进制下载后的字节数与 SHA-256 均与远端一致；`evidence-index.json` 中 20/20 个工件的存在性、字节数和 SHA-256 也全部重新计算匹配，0 个 mismatch。
- 使用 `manifest_candidate.py` 的精确 NUL/换行聚合算法对实际目录重新枚举：baseline 为 217 文件、聚合 SHA-256=`C0BA203D6A8D8A7CFD0270A7EC48CD0849470B9EA96E28E3EF65A368D81D9ABC`；candidate 为 218 文件、聚合 SHA-256=`1F506D242FB3CB504610308703A985634DC60CAD34D95C1C36175CFFE5F97BD4`。candidate 的 218 个逐文件 path/bytes/SHA、顺序和聚合值与 `candidate-after.json` 全部一致，0 个 mismatch。
- baseline 与 candidate 的实际差异恰好 2 项，与 `candidate-changes.json` 一致：`repository/ddm4ip/degradations/blur.py` 从 `D068F0B95F8D37822C8337446B881C9997445B833FD7D51E99EB46AF98C769CD` 变为 `A3CEF4FC32DE3C3ADE406C6FBDCAFAFB9E080574EE8D0A3F767E8C2AAE45CB05`；新增 `repository/tests/test_motion_blur_rng.py`，SHA-256=`00B0A2CADD361837590C5A8DC2A3629F6C53CB62605B733667193083C868566A`。
- 独立聚合复算的第一次临时脚本把 NUL/换行分隔符误写成字面量 `\0`/`\n`，因此曾得到错误聚合值；当时逐文件 218/218 已匹配。发现后按生成器源码的精确字节算法纠正，baseline/candidate 聚合值均与冻结清单一致。该验收脚本错误没有写入或改变任何远端工件。

### RED/GREEN、完整 CPU 与 kernel 门

- RED 原始日志 SHA-256=`27826223248C4BDE65DDFEA559CF740981965CC93492A7FA677479043979745C`：3 项运行、退出码 1，只有 `test_generation_does_not_change_numpy_global_random_sequence` 失败；同 seed 位级一致与官方 32×32 核有限/非负/归一化两项已通过。GREEN 原始日志 SHA-256=`017BD144AACCD9E44E0C1A9073F69FD1F5C0E5D3ED13D52CE4A4B215960B99DB`：同 3 项全部通过、退出码 0。
- 完整 `final-all.log` 已逐行完整读取并核对，SHA-256=`1A359B51982BA5A1A30A18518EE729E3D9DD4910BC1CB5468C16C854DAA12E12`；结尾为 `Ran 126 tests in 30.912s`、`OK (skipped=5)`、`IMPORT_ISOLATION_OK 81`。5 项均为既有 CUDA 条件跳过；harness 记录 `CUDA_VISIBLE_DEVICES=-1`、网络 socket 禁止和 HF/Transformers 离线。
- 新鲜独立 CPU 只读核验再次设置 `CUDA_VISIBLE_DEVICES=-1`，实际 `torch.cuda.is_available()=false`。冻结 `kernel-gt.pt` 文件 SHA-256=`4E292CA42C026965EF9B6D16CACEC83091DFC2E461C2C6788C6FDC690F832A7A`；冻结、修复前 evidence、修复后 evidence 和当前 candidate 生成张量的 tensor SHA-256 均为 `C9B12867CE2B271084B1A48CF871BD0585ADDF23C7FEC2D755F0D136F6495C11`，四者逐字节相等。candidate 生成核形状为 `1×1×32×32`、有限、非负、sum=`1.0`，且调用前后 NumPy RNG state 完全相同。

### 阻塞项与准入结论

- candidate 代码内容、218 文件冻结、仅两项文件级变化、RED/GREEN/完整 CPU 证据、冻结 benchmark 文件 SHA 与 tensor SHA 门均通过独立验收。实现保证单线程/串行调用返回后恢复 NumPy 全局 RNG state；测试未证明并发线程在调用期间不会观察到临时全局 seed，这是后续部署评审应保留的边界。
- 但冻结的 `evidence\candidate.patch` 不是可应用的 unified patch：它把 `blur.py` 的 EOF 无换行旧行与新增换行后的新行粘在同一物理行，随后直接进入第二个文件 header。对冻结 baseline 执行只读 `git apply --check --whitespace=nowarn --unsafe-paths candidate.patch` 得到 `error: corrupt patch at line 29`，退出码 `128`。这不否定 candidate 目录中的实际代码和测试结果，但说明交付补丁工件损坏。
- 因此本轮结论为：**candidate 代码/测试验收通过，但尚不满足“可另行申请 live 部署评审”的无条件准入门**。在补丁工件修复并重新冻结前，不得部署、不得把本轮写成部署就绪，也不得用手工复制绕过该工件缺口。
- 下一阶段必须在新对话单独授权“只修复验收工件、不改 candidate/live”：保留当前坏补丁作为诊断证据，从冻结 baseline 与 candidate 生成新的有效 patch/新 evidence 版本；要求 `git apply --check` 退出码 0，并在一次性隔离副本中应用后重新得到 218 文件、聚合 SHA-256=`1F506D242FB3CB504610308703A985634DC60CAD34D95C1C36175CFFE5F97BD4` 和恰好两项变化，再更新 evidence index 与 WORKLOG。该证据修复通过后，live 部署评审仍需之后另一个新对话单独明确授权，并按逐文件 CAS/hash、训练终态和 runner/spec 迁移边界执行。
- GPU 验收、精确恢复实现、Step 2/3、正式评估和数据处理均不在下一工件修复阶段授权内。当前 Step 1 full 仍只保留上述一次 `Running` 快照，不得据此判断终态。

### 清理清单与下一对话提示

## 2026-09-21：Step 2 seed0 FAILED 根因审计、checkpoint 修复与隔离重跑

### 旧 FAILED 运行根只读审计

- 按本轮启动核验重新确认远端主机为 DESKTOP-KBM1345，仓库为 D:\Unsupervised Imaging Inverse Problems；既有 Git 修改全部保留。旧运行根 D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step2-pilot-seed0 未写入、未删除、未重启。
- 旧任务 DDM4IP-BDD100K-SYNTH-Step2-Pilot-seed0 的 scheduler 状态为 Ready，LastTaskResult=1，匹配项目 runner/训练进程数为 0。status-history.jsonl 按完整 JSON 对象解析为严格 RESERVED -> RUNNING -> FAILED，无重复终态；status.json 为 FAILED、exit_code=1。
- 旧根只读证据哈希：status.json=6330456A6E427038B9DD6597EA2ADABF2AEDB2B2702D81C4852C116C16222496；status-history.jsonl=73A93157F43D14BF68532C1793A7DD8E772930BDAF5AEF246BBB8F8E92F3147C；完整 task.log=F7C45BACF1A3958A51AFB73FFF98B622B1EC5CF457F7C394DF8CB8E544C42279；command.json=D833CDA9EB6838947725FE90860F12BF61013E721D1AEDE9EE29CA30CAC11D6；spec.json=1C1D8C2C8D6B4E6909E4AB638EA220C0607EA88A1CFC448C34D9DE833C6A2652。
- 完整日志显示实际 child command 为 Step 2 seed0、batch_size=32、n_accum_steps=1、max_steps=2048、max_val_batches=0，没有 kernel_gt；训练已打印 terminal step 2048，随后在 BaseTrainer.maybe_save_checkpoint(force=True) 的 copy.deepcopy(model) 处失败：RuntimeError: Only Tensors created explicitly by the user (graph leaves) support the deepcopy protocol...
- 旧 checkpoints 只有未发布临时文件 training-state-2048.pt.41c8e0445f954cad958885e9f7068051.tmp，字节数 67258584、SHA-256=7720630C1C7BA8B4E6F024F9260A7982434213B1E6EB403DF529C940370D4BEC。独立 torch.load(map_location=cpu) 读出内部 global_step=2048、kernel_nn 状态为 dict、525 个张量且 0 个非有限张量；正式 training-state-2048.pt 和 network-snapshot-2048.pkl 均不存在，因此旧根没有可放行的终点 pair，也不能补写成功状态。
- 根因链已定位到 DirectKernel 前向将带 autograd 图的非叶子 degradation.filter 留在模型对象中；终点 snapshot 的普通深拷贝在保存阶段触发上述 PyTorch 错误。不是数据 preflight、前序 checkpoint、NaN/Inf 或 scheduler 失败。

### 修复与无训练验证

- 先新增 RED 回归测试 tests/test_checkpoint_nonleaf_filter.py，复现非叶子 filter 在 snapshot 保存时失败；只修改 ddm4ip/trainers/base.py，在 snapshot 副本深拷贝时递归收集并以 detached clone 替换非叶子运行时 Tensor，保持 live model 和梯度路径不变。当前该文件 SHA-256=BC200B678A10F805C17933E7F39A25BC2C79E68824A8FD2D2D028FDDD233B5EB。
- 远端固定 Python 下目标测试与终点保存/配置回归共 9 项全部通过、退出码 0；实际生成并加载 training-state-2048.pt 与 network-snapshot-2048.pkl 的新测试通过。全量 75-test 尝试日志 D:\DDM4IP-runtime\temp\step2-seed0-rerun-fix-20260921\full-unittest.log SHA-256=9066254281D94CBA4E45DB257040DA0CFFFA45A3FA68DC2D73540A3907BCE393，其中 6 项是当前既有非法 SHA-256 夹具/强制无 CUDA 环境问题，与本修复无关；未把该全量结果写成通过，也未捆绑无关修改。

### 隔离新 spec、preflight 与计划任务

- 新外部 spec D:\DDM4IP-runtime\experiments\phaseF-step2-pilot-spec-20260921-seed0-rerun-20260921.json SHA-256=C814F9505538DD68A58F56B15C9F44B17CD263C08DC4AA936BAE591076D4E992；新 run root 为 D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step2-pilot-seed0-rerun-20260921，新任务名为 DDM4IP-BDD100K-SYNTH-Step2-Pilot-seed0-rerun-20260921。旧 spec、旧任务和旧 run root 未复用。
- 新鲜 preflight 重新核对 benchmark summary/pairs/kernel 哈希分别为 97F874E8497F4F8FB2C814B814C15E3C43CC736AFC344DF449E58C99D58A346E、3C86E1B8CC419E6FDB627EB60D7C6DD209015123EEC44F790D0115B39BFFF9E4、4E292CA42C026965EF9B6D16CACEC83091DFC2E461C2C6788C6FDC690F832A7A；Step 1 前序 .pt 经 SHA、内部步数、flow_nn 与全量有限性复核后注入。runner SHA-256=578A956C2696BBE9650C1E1551DB60EBECF7DF8457EAE35FA18837045CEC3ABC；生成的 Step 2 command SHA-256=BCAE76C8FD966483DD6EF7DC81D6E9FC005E4AA9237E86ADBA268701F31F2336；Hydra --cfg job --resolve 退出码 0，启动前新 run root 不存在。
- 仅通过计划任务 wrapper 启动一次新 pilot；launcher 退出码 0。启动后一次性快照：任务 Running，LastTaskResult=267009 (0x41301，运行中)，匹配 runner PID=27588，新 status.json 为 RUNNING，status-history.jsonl 已有 RESERVED -> RUNNING，task.log 已记录 reserved; execution has not started 与 execution started; preflight pending。这只是运行中快照，不是成功终态。

### 阶段边界与清理清单

- 本轮只重跑 Step 2 seed0 pilot；禁止启动 Step 2 full、其他 seed、Step 3、正式评估或第二个重跑。旧 FAILED 根及其全部日志/checkpoint 临时文件作为不可变诊断证据保留。
- 用户可在 group-pc 本机 PowerShell 查看：
  Get-Content -LiteralPath 'D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step2-pilot-seed0-rerun-20260921\status.json'
  和
  Get-Content -LiteralPath 'D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step2-pilot-seed0-rerun-20260921\task.log' -Tail 50 -Wait
 ；按 Ctrl+C 只停止日志跟随，不停止计划任务。新 run root 进入终态后，必须在新对话重新做 scheduler、history、完整 task.log、command/spec、终点 pair 哈希、内部 global_step=2048/2049、kernel_nn 和全量张量有限性独立验收，未通过不得进入 Step 2 full。
- 本轮新增运行/辅助工件均在 D:\DDM4IP-runtime\experiments\phaseF-step2-pilot-spec-20260921-seed0-rerun-20260921.json、新 run root 和 D:\DDM4IP-runtime\temp\step2-seed0-rerun-fix-20260921；本机传输暂存位于 D:\DDM4IP-local-runtime\step2-seed0-rerun-fix-20260921，不作为项目运行位置，后续按精确路径清理。

### 下一对话提示

请先按 AGENTS.md 完成完整启动核验，读取本机与远端最新 WORKLOG；仅只读独立验收 D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step2-pilot-seed0-rerun-20260921。核对任务 DDM4IP-BDD100K-SYNTH-Step2-Pilot-seed0-rerun-20260921 的 scheduler/LastTaskResult/进程、status.json、按 JSON 对象边界解析的 status-history.jsonl、完整 task.log、command.json/spec.json，以及 training-state-2048.pt 和 network-snapshot-2048.pkl 的 SHA-256、内部 global_step=2048/2049、kernel_nn 和全量 Tensor 有限性。旧 FAILED 根 ...seed0 仅作不可变对照，不得覆盖、删除、重启；验收未通过不得启动 Step 2 full、Step 3 或正式评估。

- 本轮新增本机只读下载/复核目录 `D:\DDM4IP-local-runtime\audit\20260920-numpy-rng-isolation-readonly`，含远端 WORKLOG 修改前副本与指定 evidence/log 快照；项目专用，未安装包、未写公共缓存，后续只能按精确路径人工清理，不得递归批量删除。远端 audit root 未新增验收脚本或结果文件。
- 可复制的新对话提示：

> 请先按 AGENTS.md 完成完整启动核验，完整读取本机与远端最新 WORKLOG；本次只授权修复 `D:\DDM4IP-runtime\code-audit\20260920-numpy-rng-isolation` 的损坏补丁验收工件，不得修改 baseline、candidate、live 仓库、训练运行根或 benchmark。保留现有 `evidence\candidate.patch` 及其 `git apply --check` 失败证据，新建版本化 patch/evidence；独立要求 patch 对冻结 baseline `git apply --check` 退出码 0，并在一次性隔离副本应用后复算为 218 文件、总 SHA-256 `1F506D242FB3CB504610308703A985634DC60CAD34D95C1C36175CFFE5F97BD4`、恰好两项变更，再更新 evidence index 和远端 WORKLOG。本阶段不部署、不用 GPU、不启动或干预计划任务、不实现精确恢复、不进入 Step 2/3；live 部署评审仍须之后新对话单独授权。
### 清理清单与下一对话提示
---

## 2026-09-21：Step 2 live runner candidate 部署核验与 seed0 pilot 启动

### 启动核验、部署前后证据与无训练门

- 本轮重新完成启动核验：SSH 远端 `hostname=DESKTOP-KBM1345`；目标仓库为 `D:\Unsupervised Imaging Inverse Problems`；远端 `main` 分支既有工作区修改全部保留，未执行提交、推送、拉取、切换或覆盖；远端 `WORKLOG.md` 修改前 SHA-256=`92FA9C2A58AC5370B06A4839F688485B4761F2884A424B54AAC0AD4496DC236B`，本轮以远端日志为事实源。
- Fresh candidate CPU/no-training audit 使用固定远端解释器 `E:\Anaconda3\envs\ddm4ip\python.exe`，结果为 `Ran 123 tests`、`OK (skipped=5)`、`IMPORT_ISOLATION_OK 80`、0 failures；证据日志为 `D:\DDM4IP-runtime\code-audit\20260919-systematic\evidence\candidate-session5-20260921.log`。这只是无训练验收，不替代 pilot 终态验收。
- Step 1 predecessor 做了新的独立终端验收：`training-state-5242880.pt` SHA-256=`C140A210749E420DD90B4E5730EE2DEE824A5716C0972B953283225225EE6244`，内部 `global_step=5242880`；`network-snapshot-5242880.pkl` SHA-256=`80A2A591C9E2C15D41D62DE3271516E3F242193D62CBCB80A32C5AE08D3CC250`，内部 `global_step=5242881`；二者均包含 `flow_nn` 且全量张量有限。Step 1 状态为 `SUCCESS`，历史按 JSON 对象边界解析为 `RESERVED -> RUNNING -> SUCCESS`，task.log SHA-256=`E260045DE4C2B9B5E3CE873B01BE92C4DE9146E0E3DBE5DED7C39607F7A8F72A`。
- 当前 live candidate v5 冻结为 21 个 runtime/runner 文件。部署前 CAS manifest `candidate-step2-live-product-v5-manifest.json` SHA-256=`27A18F736F322E6C789149F47136E76F5AA25888DBC32B854B6C69F8C7D06210`；patch SHA-256=`97F0E358D6B2B3ACE03EDE464C053DEA9002A0FC15F8B3903CF3F50C4D41ABBF`，大小 63,262 字节。Windows baseline 为 CRLF、candidate 物料为 LF，普通 patch 重放会因换行边界失败；本轮保留 v1–v3 失败诊断，冻结 baseline-compatible materialized bytes，以 `git apply --check --ignore-whitespace` 通过并用归一化字节校验，未用手工复制绕过。部署 receipt `live-deployment-step2-v5-20260921.json` 为 `status=SUCCESS`、`entry_count=21`，明确记录“仅部署、未启动任务”。
- 部署后立即做了新的 live hash/CAS 验收，21/21 目标文件均与冻结 materialized candidate 和 receipt 一致；未部署测试文件或 Step 3 配置。live no-training verify 为 PASS：真实 Step 2 Hydra 命令只出现一个 `training.seed=0` 和一个 `training.max_val_batches=0`，不含 `kernel_gt`；冲突 seed 和非零 `max_val_batches` 分别被拒绝并返回 `Step 2 training.seed must match the frozen spec seed`、`Step 2 requires training.max_val_batches=0`。PyTorch `2.4.1+cu118` 上实际构造并 state_dict round-trip `DirectKernel`，公共 pre-hook 不可用时走 fallback，missing/unexpected 均为空，核有限且 sum=`0.9999991059303284`。Hydra `--cfg job --resolve` 退出码 0，日志 SHA-256=`F75156ABCC8801158763A42B6A9ED794C9FEEF9828B4ABCB659857A34CAEB7D`。

### Step 2 seed0 pilot 准入与启动

- pilot 外部冻结 spec 为 `D:\DDM4IP-runtime\experiments\phaseF-step2-pilot-spec-20260921-seed0.json`，SHA-256=`4CA627BED62A053CBFDB20F82F58F9CD6A6C613B8A4CFB11B6B4141E49AF6F33`；run root 为 `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step2-pilot-seed0`，任务名为 `DDM4IP-BDD100K-SYNTH-Step2-Pilot-seed0`。benchmark fresh hashes：`summary.json`=`97F874E8497F4F8FB2C814B814C15E3C43CC736AFC344DF449E58C99D58A346E`，`test-paired/pairs.jsonl`=`3C86E1B8CC419E6FDB627EB60D7C6DD209015123EEC44F790D0115B39BFFF9E4`，`degradation/kernel-gt.pt`=`4E292CA42C026965EF9B6D16CACEC83091DFC2E461C2C6788C6FDC690F832A7A`；Step 2 clean 文件和清单均为 100，角色无重叠。预启动验证为 PASS，且启动前任务与 run root 均不存在。
- 仅通过已部署 wrapper 启动一次 seed0 pilot：`batch_size=32`、`n_accum_steps=1`、`max_steps=2048`、`max_val_batches=0`，前序为明确的 Step 1 `.pt`；没有启动 full、Step 3 或正式评估。启动器退出码为 0，单次启动后快照显示任务 `Running`、`LastTaskResult=267009 (0x41301，表示仍在运行)`，`status.json` 为 `RUNNING`；远端固定 Python 进程存在，task.log 已由 718 字节增长到 9,345 字节且时间戳更新。该快照不是成功或失败终态，不能写成 pilot 已完成。

### 当前阶段边界、验收准入与清理清单

- 本轮只授权并执行了 Step 2 seed0 pilot 启动；禁止 Step 2 full seeds 0–4、Step 3、正式评估和任何额外训练/评估任务。pilot 结束后必须在新的远端 SSH 进程中独立交叉核验计划任务状态与 `LastTaskResult`、匹配进程、`status.json`、按 JSON 对象边界解析的完整 `status-history.jsonl`、完整 `task.log`、`command.json/spec.json`，以及终点 `training-state-2048.pt`/`network-snapshot-2048.pkl` 的 SHA-256、内部 `global_step=2048/2049`、`kernel_nn` 和全量张量有限性；任一项不满足就保留证据并报告，不得重跑或覆盖。
- 只有上述 seed0 pilot 独立终态验收 PASS 后，才可在新的对话中申请 Step 2 full seeds 0–4；本日志不授权该下一阶段。
- 清理清单：远端既有并本轮新增证据均位于 `D:\DDM4IP-runtime\code-audit\20260919-systematic\`；外部 spec `D:\DDM4IP-runtime\experiments\phaseF-step2-pilot-spec-20260921-seed0.json` 和 pilot run root 为本项目专用、需保留的运行证据；本机辅助文件位于 `D:\DDM4IP-local-runtime\`。本轮不删除任何文件或目录。

## 2026-09-21：Step 2 seed0 pilot 独立终态验收暂未进入终态

### 新鲜只读核验

- 本轮重新完成启动核验：`ssh group-pc hostname` 返回 `DESKTOP-KBM1345`；远端仓库 `D:\Unsupervised Imaging Inverse Problems` 的 `main` 工作区既有 `AM/M/??` 修改全部保留，未执行 Git 写操作；本轮未重跑、重启、覆盖或删除 seed0 pilot。
- 对任务 `DDM4IP-BDD100K-SYNTH-Step2-Pilot-seed0` 的新鲜调度器快照显示 `State=Running`、`LastTaskResult=267009 (0x41301)`、`NumberOfMissedRuns=0`；匹配项目 Python 进程仍存在：runner PID `6244`，训练 PID `23800`。因此本轮不能把它当作终态，也没有等待或干预任务。
- `status.json` 仍为 `RUNNING`，状态文件 SHA-256=`5F0574CCB843E5D8260C6A53D19E393AC67A66E694659596080318A1472536D6`；`command.json` SHA-256=`D833CDA9EB6838947725FE90860F12BF61013E721D1AEEDE9EE29CA30CAC11D6`，明确包含 `training.seed=0`、`training.max_steps=2048`、`training.max_val_batches=0`，且命令中没有 `kernel_gt`；reserved `spec.json` SHA-256=`1C1D8C2C8D6B4E6909E4AB638EA220C0607EA88A1CFC448C34D9DE833C6A2652`，明确为 `stage=step2`、`mode=pilot`、`seed=0`、`training.max_val_batches=0`。
- 因任务仍在运行，本轮未将 `status-history.jsonl`、完整 `task.log` 或终点 `training-state-2048.pt`/`network-snapshot-2048.pkl` 宣布为终态证据，未执行终点 SHA-256、内部 `global_step=2048/2049`、`kernel_nn` 和全量张量有限性放行。
- 已生成的 `.hydra/config.yaml` 只读相关字段显示 `dataset.train` 与 `dataset.test` 均指向 `${paths.data}/step2-clean/clean`，且均为 `need_clean=true`、`need_noisy=false`；`overrides.yaml` 仅记录 `training.seed=0` 与 `training.max_val_batches=0`，没有 `kernel_gt` 训练覆盖。`spec.json` 中的 `kernel_gt` 仅是 benchmark 元数据路径，不能解读为训练命令注入。

### 阶段边界与下一步

- 结论仅为“终态验收尚不能进行”，不是 PASS 或 FAILED；所有现有运行证据继续保留。不得重跑或重启该 pilot；不得启动 Step 2 full seeds 0–4、Step 3 或正式评估。
- 用户在新的对话中确认任务已自然进入终态后，才重新执行一次完整独立验收；只有所有终态门通过后，才可在之后新的对话中申请 Step 2 full seeds 0–4。

## 2026-09-21：Step 2 seed0 pilot 自然结束但进入 FAILED 终态（仅状态快照）

- 新的远端只读快照时间为 `2026-09-21T17:42:57.4468179+08:00`，主机仍为 `DESKTOP-KBM1345`；Scheduled Task 已为 `Ready`，`LastTaskResult=1`，最后运行时间为 `2026-09-21T16:18:37+08:00`，匹配 runner/训练 Python 进程数为 `0`。
- `status.json` 当前为 `FAILED`、`exit_code=1`，更新时间为 `2026-09-21T09:15:36.694033+00:00`。本条只记录终态发现，不替代后续对 `status-history.jsonl`、完整 `task.log`、command/spec 和 checkpoint pair 的独立失败证据审计。
- 本轮未重跑、未重启、未覆盖或删除 seed0 pilot；不得启动 Step 2 full seeds 0–4、Step 3 或正式评估。下一步必须在新的对话中只读审计该 FAILED 运行根并报告根因；不得以失败 pilot 申请后续 full 阶段。

### 清理清单与下一对话提示

## 2026-09-21：Step 2 seed0 重跑当前运行中（追加索引）

- 旧 FAILED 根只读审计、非叶子 Tensor snapshot 根因、base.py 修复、9 项目标回归、benchmark/前序 checkpoint/Hydra preflight 和新计划任务启动已记录于本文件本轮条目；旧根保持不可变。
- 新任务 DDM4IP-BDD100K-SYNTH-Step2-Pilot-seed0-rerun-20260921 当前仅有 RUNNING 快照，不能写成成功；终态必须由新对话按 checkpoint pair、内部步数、kernel_nn 和全量有限性独立验收。

## 2026-09-21：Step 2 seed0 重跑停滞诊断、策略修复与第二个独立重跑

- 对第一重跑根 `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step2-pilot-seed0-rerun-20260921` 做了保留证据的停滞诊断：训练进程在首个 `DataLoader` batch 前等待，GPU 利用率低且训练 CPU 时间不增长。远端同配置探针 `D:\DDM4IP-runtime\temp\step2-seed0-stall-audit-20260921\dataloader_probe.py` 的 SHA-256=`A86A9E5046BA88D70E127EC3F758A7EA0A54C0327A64F0DE8CEF0116632DBC34`；`num_workers=4` 首 batch 在 90 秒超时，`num_workers=0` 首 batch 在 0.7096 秒成功，数据集长度 1024、batch shape=`[32,3,256,256]`。因此本次停滞根因是 Windows DataLoader 多进程 worker 配置，不是 GPU、checkpoint 或训练预算问题。
- 已停止第一重跑的计划任务并确认匹配进程数为 0；该根及最初 FAILED 根均未改写。第一重跑保留 `Stop-ScheduledTask` 结果 `LastTaskResult=267014`，不得作为成功或失败训练产物使用。
- 为防止同类停滞再次发生，远端 live runner `scripts/bdd100k_synthetic_runner.py` 已加入 Step 2 策略门：缺少 `training.num_workers` 时强制注入 `training.num_workers=0`，显式非零值直接拒绝并报 `Step 2 requires training.num_workers=0 on Windows`。当前 runner SHA-256=`892703F552373BBED00C30B57E7C37171A5F9D33FF588E3CF63077EA0D187FAB`。新增的默认注入/非零拒绝回归测试均通过；此前非叶子 Tensor checkpoint 修复仍保持通过。
- 新建且未覆盖旧证据的第二重跑：外部 spec `D:\DDM4IP-runtime\experiments\phaseF-step2-pilot-spec-20260921-seed0-rerun2-20260921.json`，SHA-256=`85CE9F83A3A881B15FBF5B0F11DD377F302EFD3ECEA66389AF656348E6BD6FBA`；run root `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step2-pilot-seed0-rerun2-20260921`；任务 `DDM4IP-BDD100K-SYNTH-Step2-Pilot-seed0-rerun2-20260921`。冻结预算仍为 `max_steps=2048`、`batch_size=32`、`n_accum_steps=1`、`max_val_batches=0`；另设 `report_every_steps=128`、`save_every_steps=512`，不增加训练预算。启动前 command SHA-256=`6F33BFE036855B5EFE1CB517E5B1DE632B9902F0620711ECAA922580DE397CDE`。
- 新重跑已由计划任务接管；启动后唯一快照：`State=Running`、`LastTaskResult=267009 (0x41301，运行中)`，匹配 runner PID=`25428`；新根 `status.json=RESERVED`、`status-history.jsonl=RESERVED`、`task.log` 为 37 字节的 `reserved; execution has not started`。这是启动确认，不是终态成功。后续必须由新 SSH 进程独立验收 scheduler/LastTaskResult/进程、status/history、完整 task.log、command/spec、终点 pair SHA-256、内部 `global_step=2048/2049`、`kernel_nn` 和全量张量有限性；任一项不满足都不得进入 Step 2 full。

### 下一对话提示

请先按 `AGENTS.md` 完成完整启动核验，读取本机与远端最新 `WORKLOG.md`；本次只读独立验收 `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step2-pilot-seed0-rerun2-20260921` 和任务 `DDM4IP-BDD100K-SYNTH-Step2-Pilot-seed0-rerun2-20260921`。核对 scheduler/LastTaskResult/匹配进程、`status.json`、按 JSON 对象边界解析的完整 `status-history.jsonl`、完整 `task.log`、`command.json`/`spec.json`；终态时必须同时核对 `training-state-2048.pt` 与 `network-snapshot-2048.pkl` 的 SHA-256、内部 `global_step=2048/2049`、`kernel_nn`、`flow_nn` 模型键以及所有张量有限性。旧 FAILED 根和第一重跑根只作不可变对照，不得覆盖、删除、重启或把单个 SUCCESS/退出码当作通过；未通过终态验收不得启动 Step 2 full、Step 3 或正式评估。若仍在运行，只报告新鲜快照，不持续轮询。

## 2026-09-21：Step 2 seed0 rerun2 新对话启动核验与一次性快照（仍在 preflight）

### 启动核验与静态门禁

- 本轮先完整读取本机 `WORKLOG.md`，并通过 `ssh group-pc` 核验远端主机为 `DESKTOP-KBM1345`、仓库为 `D:\Unsupervised Imaging Inverse Problems`；远端 `main` 工作区既有 `AM/M/??` 修改全部保留，未执行 reset、checkout、覆盖、删除、提交或其他 Git 写操作。远端 `WORKLOG.md` 下载前 SHA-256=`EA4A9A3A00A29D945E82DC215050BB3D69A6865B37645DDF292B54811B561CD1`，与下载副本一致。
- 旧 FAILED 根 `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step2-pilot-seed0` 和第一次停滞重跑根 `D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step2-pilot-seed0-rerun-20260921` 均仍存在；本轮未写入、未删除、未重启或复用。
- 指定 retry2 external spec 已存在，SHA-256=`85CE9F83A3A881B15FBF5B0F11DD377F302EFD3ECEA66389AF656348E6BD6FBA`；live runner SHA-256=`892703F552373BBED00C30B57E7C37171A5F9D33FF588E3CF63077EA0D187FAB`。benchmark `summary.json`/`test-paired/pairs.jsonl`/`degradation/kernel-gt.pt` SHA-256 分别为 `97F874E8497F4F8FB2C814B814C15E3C43CC736AFC344DF449E58C99D58A346E`、`3C86E1B8CC419E6FDB627EB60D7C6DD209015123EEC44F790D0115B39BFFF9E4`、`4E292CA42C026965EF9B6D16CACEC83091DFC2E461C2C6788C6FDC690F832A7A`。
- Step 1 predecessor `training-state-5242880.pt`/`network-snapshot-5242880.pkl` 新鲜 SHA-256 分别为 `C140A210749E420DD90B4E5730EE2DEE824A5716C0972B953283225225EE6244` 和 `80A2A591C9E2C15D41D62DE3271516E3F242193D62CBCB80A32C5AE08D3CC250`，与 external/reserved spec 声明一致。
- external/reserved spec 的冻结覆盖包含 `batch_size=32`、`n_accum_steps=1`、`max_steps=2048`、`max_val_batches=0`、`num_workers=0`、`report_every_steps=128`、`save_every_steps=512`；spec 中的 `kernel_gt` 仅为 benchmark 元数据路径，未作为训练 override 注入。retry2 的 run root 和 Scheduled Task 已在前一阶段创建，故本轮发现其已存在，未尝试重新满足“不存在”门禁或再次启动。

### 一次性远端运行快照

- Scheduled Task `DDM4IP-BDD100K-SYNTH-Step2-Pilot-seed0-rerun2-20260921` 为 `Running`，`LastTaskResult=267009 (0x41301)`，最后运行时间为 `2026-09-21 21:43:42`；该码只表示仍在运行，不能解释为成功。
- 匹配进程仅有 stage wrapper PID=`25428` 和 synthetic runner PID=`15228`；未发现训练进程。`status.json` 为 `RUNNING`，SHA-256=`58AC5DD76A5DEC1C7E5DB1BC87958A46DB087086456EBAB9426C627401D2C4E8`；`status-history.jsonl` 为 `RESERVED -> RUNNING` 两个完整对象，SHA-256=`EB558516EF5EEBDAAE0D896988E7E747901BB081EC6EA481A7B1F28E462C8AC2`。
- `task.log` 当前为 75 字节，SHA-256=`2CE479ED5756C1131976840997C3DA17316A26D8E0130552FAFEB2D9FB6EB8DA`，内容只有 `reserved; execution has not started` 与 `execution started; preflight pending`；最近写入时间为 `2026-09-21T21:59:21.0239304+08:00`。`command.json` 不存在，`checkpoints` 目录不存在；因此当前尚不能核对实际 command 的 `training.num_workers=0` 或 command-level `kernel_gt` 注入，也没有任何终点 checkpoint。
- 当前证据把边界精确定位在“runner 已进入 execute，但仍停在 preflight pending，尚未生成 command 或训练子进程”；本轮没有足够证据把它归因于具体 Hydra/依赖错误，也没有等待、停止、重启、覆盖或创建第三个重跑。

### 阶段边界与下一步

- 本轮结论不是成功，也不是终态 FAILED；retry2 尚在运行且未进入首 batch。不得把 `LastTaskResult=267009`、`RUNNING` 或启动器退出码当作成功，不得启动 Step 2 full、其他 seed、Step 3 或正式评估。
- 用户可在 `group-pc` 本机 PowerShell 查看：

```powershell
$task='DDM4IP-BDD100K-SYNTH-Step2-Pilot-seed0-rerun2-20260921'
$run='D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step2-pilot-seed0-rerun2-20260921'
Get-ScheduledTask -TaskName $task | Get-ScheduledTaskInfo
Get-Content -Raw -LiteralPath "$run\status.json"
Get-Content -LiteralPath "$run\task.log" -Tail 50 -Wait
```

按 `Ctrl+C` 只停止日志跟随，不会停止计划任务。下一次新对话在任务自然进入终态后，必须重新完成 scheduler/进程、status、完整 JSON 对象边界 history、完整 task.log、command/spec、终点 pair SHA-256、内部 `global_step=2048/2049`、`kernel_nn`/`flow_nn` 及全量 Tensor 有限性独立验收；任何缺项均报告失败根因并保留证据，不创建第三个重跑。

- 本轮新增/保留的只读辅助脚本为远端 `D:\DDM4IP-runtime\temp\step2-seed0-rerun2-snapshot-20260921.ps1`，4855 字节，SHA-256=`F557BF2E36BB746BAD0F70A75243B0E2F5760A5916F6C860C8021DE71208817F`；本机传输副本位于 `D:\DDM4IP-local-runtime\readonly-startup-20260921\step2_retry2_snapshot.ps1`，未运行项目代码，未安装依赖，未删除任何证据。
- 为补充静态门禁，本轮以远端固定 Python 执行 `ddm4ip.main ... --cfg job --resolve`，覆盖同一 Step 2 seed0 预算和 `training.num_workers=0`；30 秒内无输出、无退出码，解析日志 `D:\DDM4IP-runtime\temp\step2-rerun2-hydra-resolve-20260921\hydra-resolve.log` 为 0 字节，并观察到临时诊断 PID=`14476`。该命令未作为通过证据；PID 已确认与 Scheduled Task 不同且在后续清理检查时不存在，未停止 retry2 wrapper/runner。Hydra 解析门因此在本轮保持未通过/未闭合，不能把 retry2 报告为成功。
## 2026-09-22: Step 2 seed0 retry2 completed training but strict terminal acceptance failed
- Fresh read-only startup verification confirmed DESKTOP-KBM1345; the remote repository remains main with all pre-existing AM/M/?? changes preserved. No reset, checkout, overwrite, delete, or Git write was performed.
- The retry2 Scheduled Task DDM4IP-BDD100K-SYNTH-Step2-Pilot-seed0-rerun2-20260921 is Ready, LastTaskResult=0, and has no matching runner/training process. status.json is SUCCESS with exit_code=0.
- Complete status-history.jsonl was parsed by JSON object boundaries as exactly RESERVED -> RUNNING -> SUCCESS. The complete 13,035-byte task.log contains the terminal Training finished at step 2048 and execution finished: status=SUCCESS exit_code=0; the independent exception/nonfinite scan found zero suspicious lines.
- Frozen input hashes re-verified: external spec 85CE9F83A3A881B15FBF5B0F11DD377F302EFD3ECEA66389AF656348E6BD6FBA; runner 892703F552373BBED00C30B57E7C37171A5F9D33FF588E3CF63077EA0D187FAB; benchmark summary/pairs/kernel 97F874E8497F4F8FB2C814B814C15E3C43CC736AFC344DF449E58C99D58A346E / 3C86E1B8CC419E6FDB627EB60D7C6DD209015123EEC44F790D0115B39BFFF9E4 / 4E292CA42C026965EF9B6D16CACEC83091DFC2E461C2C6788C6FDC690F832A7A; Step 1 predecessor training-state-5242880.pt / network-snapshot-5242880.pkl C140A210749E420DD90B4E5730EE2DEE824A5716C0972B953283225225EE6244 / 80A2A591C9E2C15D41D62DE3271516E3F242193D62CBCB80A32C5AE08D3CC250.
- Reserved spec/command re-verified: run root and task binding match; command contains training.num_workers=0, the fixed budget (batch_size=32, n_accum_steps=1, max_steps=2048, max_val_batches=0, report_every_steps=128, save_every_steps=512), and no kernel_gt string.
- Terminal files: command.json SHA CD46581FEE7B60C6BDF6EC08C511FC584FF43262961FBF5C7092C566CDF67E35; spec.json SHA 1C8E3180B6B1CE47D0E0B7111B6E6B30645384501777AC1DB5973A8552724C67; training-state-2048.pt SHA 7AF5CA02FCC9A2C5070964C6513E3D6E8A40E33E5F7710EA75B523F98320E6AF, internal global_step=2048; network-snapshot-2048.pkl SHA F6CC4BDDAC17C46D6645B02B9F65359108D101B74AD486C18ED0FE2818A8BA21, internal global_step=2049.
- Endpoint tensor scans found zero nonfinite tensors: 525 tensors in the .pt and 214 tensors in the .pkl; the .pt includes loss_optim, and the .pkl includes 207 parameters and 7 buffers. No .tmp or .partial files were present.
- Strict acceptance failure: .pt root keys are aux_flow_nn, prtr_flow_nn, kernel_nn, loss_optim, global_step; .pkl root keys are aux_flow_nn, prtr_flow_nn, kernel_nn, global_step, run_dir. Exact kernel_nn is present, but exact flow_nn is absent in both endpoint files. aux_flow_nn and prtr_flow_nn are not silently re-labeled as flow_nn.
- The corrected remote audit script is D:\DDM4IP-runtime\temp\step2-seed0-rerun2-acceptance-20260922-v5.py, SHA-256 recorded by the remote command. Earlier v1 audit-script failure was retained as audit-tool evidence and was not a training failure.
- Final classification: training execution completed, but this retry2 is NOT accepted under the current exact kernel_nn + flow_nn checkpoint-key contract. Preserve all roots and evidence. Do not start Step 2 full, another seed, Step 3, formal evaluation, or a third rerun without a new explicit authorization and a decision on this checkpoint-schema mismatch.

## 2026-09-22: Step 2 seed0 rerun3 launched after checkpoint schema repair

- Full startup verification was completed: local WORKLOG and read-only D:/DDM4IP-local-runtime history were inspected without writes; group-pc hostname was DESKTOP-KBM1345; remote repository status preserved all pre-existing AM/M/?? changes. No reset, checkout, delete, overwrite, or commit was performed.
- Root cause was confirmed in the live code: DiffinstructOpTrainer trains distinct aux_flow_nn and prtr_flow_nn plus kernel_nn, while BaseTrainer serialized self.models names directly. The production fix adds a checkpoint-only model-view hook; DiffinstructOpTrainer emits an independent CPU/eval flow_nn copy from aux_flow_nn while retaining aux_flow_nn, prtr_flow_nn, and kernel_nn. Training model semantics and budget are unchanged.
- Runner postflight now requires exact flow_nn and kernel_nn in both Step 2 terminal checkpoint files. Step 3 kernel loading uses a temporary repository sys.path and restores the original list after pickle loading.
- TDD and regression evidence passed remotely with fixed Python E:/Anaconda3/envs/ddm4ip/python.exe: focused checkpoint schema suite 3/3 OK; related no-training suite 35/35 OK; full unittest discover 80 tests OK (log D:/DDM4IP-runtime/temp/step2-schema-full-unittest-20260922-v3.log); Hydra --cfg job --resolve exit code 0 (log D:/DDM4IP-runtime/temp/step2-rerun3-hydra-resolve-20260922.log).
- Fresh benchmark hashes before reservation: summary 97F874E8497F4F8FB2C814B814C15E3C43CC736AFC344DF449E58C99D58A346E; test-paired/pairs.jsonl 3C86E1B8CC419E6FDB627EB60D7C6DD209015123EEC44F790D0115B39BFFF9E4; degradation/kernel-gt.pt 4E292CA42C026965EF9B6D16CACEC83091DFC2E461C2C6788C6FDC690F832A7A.
- Fresh Step 1 predecessor hashes: training-state-5242880.pt C140A210749E420DD90B4E5730EE2DEE824A5716C0972B953283225225EE6244; network-snapshot-5242880.pkl 80A2A591C9E2C15D41D62DE3271516E3F242193D62CBCB80A32C5AE08D3CC250. Independent schema verification passed with internal global_step 5242880/5242881, exact flow_nn, finite tensors, and restored sys.path. Current runner SHA-256 is 44939EC621553CB9440F6F549DC6EDABADA6A4D833942441EBDE7DE49378CD02.
- The only authorized rerun was reserved from external spec D:/DDM4IP-runtime/experiments/phaseF-step2-pilot-spec-20260922-seed0-rerun3-20260922.json, SHA-256 4371575F2E810EB5DEB0378FE2F8DF8C3D26D51B7B7477E7CE2F7AB4E8282E81, with run root D:/DDM4IP-runtime/experiments/bdd100k-synthetic-motionblur-v1-step2-pilot-seed0-rerun3-20260922 and task DDM4IP-BDD100K-SYNTH-Step2-Pilot-seed0-rerun3-20260922. Target spec, run root, and task were absent before creation; immutable old roots remain present.
- Fixed contract recorded in the spec and launch command: batch_size=32, n_accum_steps=1, max_steps=2048, max_val_batches=0, report_every_steps=128, save_every_steps=512, num_workers=0, seed=0; command contains training.num_workers=0 and no kernel_gt.
- One official prepare -> execute Scheduled Task launch was performed. The single post-launch snapshot at 2026-09-22 11:12:09 +08:00 found State=Running, LastTaskResult=267009 (0x41301), runner/training/wrapper processes present, status.json=RUNNING, status-history.jsonl=RESERVED -> RUNNING, and task.log length 9541 bytes with model initialization output. This is not a terminal PASS and no terminal acceptance has been attempted.
- Next gate: after the user reports the task has reached a terminal state in a new conversation, independently verify scheduler/process/status/history/task.log, command/spec, endpoint hashes and internal steps, exact kernel_nn plus flow_nn in both files, all tensor/optimizer finiteness, no temporary checkpoint files, and sys.path restoration. Do not rerun, reuse any old root, start full/other seed/Step 3/formal evaluation, or reinterpret a training SUCCESS as acceptance.


## 2026-09-22: Step 2 seed0 rerun3 independent terminal acceptance PASS

- Scope was limited to D:\\DDM4IP-runtime\\experiments\\bdd100k-synthetic-motionblur-v1-step2-pilot-seed0-rerun3-20260922 and Scheduled Task DDM4IP-BDD100K-SYNTH-Step2-Pilot-seed0-rerun3-20260922. No rerun, stop, old-root reuse, Step 2 full, other seed, Step 3, or formal evaluation was performed.
- Startup checks confirmed DESKTOP-KBM1345, remote repository main, and preservation of all existing AM/M/?? changes. Terminal scheduler/process snapshot: Ready, LastTaskResult=0, matching processes=0; status SUCCESS/0; complete history parsed by JSON object boundaries as RESERVED -> RUNNING -> SUCCESS; complete task.log was 13033 bytes and 234 lines with zero suspicious/nonfinite lines.
- External spec SHA-256=4371575F2E810EB5DEB0378FE2F8DF8C3D26D51B7B7477E7CE2F7AB4E8282E81; runner SHA-256=44939EC621553CB9440F6F549DC6EDABADA6A4D833942441EBDE7DE49378CD02; reserved spec SHA-256=1D2DDE062C5BB1439263BAEDC0E91BCE7FADA22B71399A389A4F18D2054EFD00; command SHA-256=EBDA72DD8B67F913133853C2376D8C913C66A7C52C30DC4FD6F017195731DA4F. Binding is stage=step2, mode=pilot, seed=0, with the target run root/task. Frozen budget is batch_size=32, n_accum_steps=1, max_steps=2048, max_val_batches=0, report_every_steps=128, save_every_steps=512, num_workers=0. Command and resolved Hydra config contain no kernel_gt; reserved spec retains kernel_gt=degradation/kernel-gt.pt only as benchmark provenance metadata, not a training override.
- Endpoint training-state-2048.pt: 84066822 bytes, SHA-256=856400A2DFC4C8966C4DFE9ADF757CEB93F81670029FC05CDF0DA57A6DF5C4CF, internal global_step=2048. Endpoint network-snapshot-2048.pkl: 50545849 bytes, SHA-256=CD92A5BA7DAA12AF2A176DCB22A118F377A1B8C7107DE08CA319EF4DA6F0B479, internal global_step=2049. Both contain exact flow_nn and kernel_nn; .pt contains loss_optim; all 630 .pt tensors and 319 .pkl tensors are finite; sys.path was restored; no .tmp/.partial files exist under the run root.
- Independent audit script D:\\DDM4IP-runtime\\temp\\step2-seed0-rerun3-acceptance-20260922-v1.py SHA-256=213FC8A7C3F415107A02284919F58DE7E165DF2FF8E38576E131302A737602F5 returned AUDIT_RESULT=PASS with Python exit code 0. Final classification is training completed and strict terminal acceptance PASS, not training failure and not training-completed-but-acceptance-failed. Old roots/evidence were preserved. Step 2 full, other seeds, Step 3, and formal evaluation remain separately unauthorized.

## 2026-09-22: Task 12 Step 2 full seed0 launched; terminal acceptance pending

- Scope is Step 2 full seeds 0-4 only, serialized on the single RTX 2070 SUPER. Seed1 is gated on seed0 natural completion and independent strict acceptance. No Step 3, evaluation, data processing, or extra task started.
- Rerun3 strict audit passed. Frozen Step 1 predecessor hashes remain C140A210...6244 (.pt) and 80A2A591...C250 (.pkl), internal 5242880/5242881, exact flow_nn, finite tensors.
- Seed0 external spec D:\DDM4IP-runtime\experiments\phaseF-step2-full-spec-20260922-seed0.json SHA-256 4F1FF359389908FBAF6F92ECEB76D0DEB0F000C1CD822A2B7D2DADA86DCC35C6; reserved spec SHA-256 ED0B382ACD0AE3A20D877711D9BF148ACA37CEB029D5045B711F0764B33565CA.
- Frozen config: seed 0, batch 32, accumulation 1, max_steps 1054720, max_val_batches 0, workers 0, report/save/plot 16384/262144/131072. Hydra preflight exited 0 (log SHA-256 17499F2B...303).
- Scheduled Task DDM4IP-BDD100K-SYNTH-Step2-Full-seed0 launched with exit 0. One existence snapshot found Running, LastTaskResult 267009, wrapper PID 26444, runner PID 21840, status RUNNING, RESERVED -> RUNNING history, and task.log written. This is launch evidence only.
- Reconnectable viewer D:\DDM4IP-runtime\orchestration\watch_bdd100k_step2_full.ps1 SHA-256 E2C18FF02D335A68135E12BF489FF3D5D16485D740AB7BC982E7EA756524FF2C passed the not-created-task regression after a minimal fix.
- Seed1-4 exact tasks, roots, and specs remain absent; Step3/evaluation task count is zero. Old failures, reruns, and pilots were not reused or modified.
- Next gate is seed0 terminal acceptance: scheduler/process/status/history/task.log, fixed budget, endpoint hashes, internal 1054720/1054721, exact flow_nn/kernel_nn, all tensor/optimizer finiteness, no temporary checkpoint, and sys.path restoration. Only PASS releases seed1.