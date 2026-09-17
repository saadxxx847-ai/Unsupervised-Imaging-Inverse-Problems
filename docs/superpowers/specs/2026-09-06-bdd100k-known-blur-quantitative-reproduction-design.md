# 自有 BDD100K 已知运动模糊定量复现实验：设计说明

**日期：** 2026-09-06  
**设计状态：** 用户已批准设计方向；本文待用户书面审核  
**实施状态：** 尚未生成数据、修改训练代码、启动 pilot、训练或评估  
**目标文档位置：** `D:\Unsupervised Imaging Inverse Problems\docs\superpowers\specs\2026-09-06-bdd100k-known-blur-quantitative-reproduction-design.md`

## 1. 决策与目标

本实验使用用户自己的 BDD100K 清晰道路图像，按照论文 *Unsupervised Imaging Inverse Problems with Diffusion Distribution Matching* 的 FFHQ 固定运动模糊协议，构造一个已知真实退化算子、训练阶段不使用成对监督、测试阶段保留清晰真值的定量实验。

最终必须能够对每张测试图像及整个测试集合法计算：

- PSNR，越高越好；
- SSIM，越高越好；
- LPIPS，越低越好。

同时报告模糊输入基线、真实核 Oracle 恢复和学习核恢复，避免把求解器问题误判为核估计问题。

本实验称为“在自有 BDD100K 数据域上复现论文的合成已知退化协议”，不能称为“复现论文 FFHQ Table 2 原始数值”。原因是图像域、测试数量、运行平台和部分工程实现与论文不同。

## 2. 与既有真实 BDD100K 主线的关系

当前既有主线使用真实、异质且不配对的模糊图：

- Step 2 保持 `training.max_val_batches=0`；
- Step 3 保持 noisy-only，`batch.clean=None`；
- 只允许报告重投影 L1/L2、输出图、核及必要的无参考诊断；
- 不允许把独立清晰目录按索引伪装成真值并计算 PSNR、SSIM、LPIPS。

本文设计的是一条新的、完全隔离的 synthetic quantitative 主线。它不得覆盖、改名、删除或静默改变既有 `step{1,2,3}_bdd100k.yaml`、数据视图或历史实验目录。两条主线的结果必须分开陈述：

1. synthetic quantitative：回答“在道路图像域和已知固定运动模糊下，DDM4IP 能否学到有用的核并恢复图像”；
2. real unpaired：回答“在真实异质模糊数据上，方法能否产生可解释、可诊断的恢复结果”。

## 3. 论文协议与本实验的对应关系

| 角色 | 论文 FFHQ | 本实验 BDD100K | 是否进入全参考指标 |
| --- | --- | --- | --- |
| Step 1 观测分布 | 1,000 张清晰图经未知于算法的固定核和噪声退化 | 1,000 张独立道路清晰图经固定真实核和噪声退化 | 否 |
| Step 2 清晰分布 | 另外 100 张清晰图 | 另外 100 张道路清晰图 | 否 |
| Step 3 测试 | 独立 FFHQ 验证清晰图及其合成退化 | 500 张独立道路清晰图及其合成退化 | 是 |
| 额外样本 | 无关 | 139 张开发/预留图 | 不进入正式结果 |

训练阶段不得向损失提供 Step 1 模糊图与其源清晰图的配对关系。真实核 `k_gt` 只允许用于生成观测、运行 Oracle 和最终核误差分析，不允许作为 Step 2 优化目标或输入。

## 4. 数据来源、冻结与划分

### 4.1 唯一数据来源

源图只来自远端当前已经筛选的清晰硬链接视图：

- `D:\DDM4IP-runtime\group-data-views\BDD100K_Blur_Sharp\train\clean`：1,565 张；
- `D:\DDM4IP-runtime\group-data-views\BDD100K_Blur_Sharp\val\clean`：174 张；
- 合计：1,739 张。

构建前必须重新验证以上数量，并为每张图记录规范化相对路径、文件名、字节数、SHA-256、宽、高和颜色通道。若数量或排序清单哈希与设计时不一致，构建器必须停止，不能沿用旧计数继续生成。

### 4.2 划分规则

先按规范化源路径排序，再使用独立的 `split_seed=42` 做确定性置换，然后按源图级别划分：

- `step1_observation`：1,000 张；
- `step2_clean`：100 张；
- `test_paired`：500 张；
- `dev_reserve`：139 张。

划分必须发生在任何裁剪、缩放或派生文件生成之前。同一源图及其任何派生物只能属于一个角色。`dev_reserve` 只用于数据链路和评估代码的 pilot，不进入最终均值，也不能在看到正式测试指标后转为调参集。

当前审计 CSV 没有视频、场景或采集来源 ID。设计只能保证源文件级互斥和 SHA-256 完全重复隔离，不能宣称完成按视频或采集来源的组隔离。可以做感知相似度的跨集合只读审计，但不得仅凭感知哈希删除文件，也不得把该审计描述为真实来源标注。

### 4.3 图像预处理

源图预期为 1280×720 RGB。为与论文 FFHQ 256×256 设置及现有小型 CFM 配置对齐，使用唯一、固定的预处理：

1. 取完整高度对应的中央 720×720 正方形，半开坐标为 `[top=0, left=280, bottom=720, right=1000]`；
2. 使用 Pillow bicubic 缩放到 256×256；
3. 转换为 RGB；
4. 保存为无额外有损压缩的 PNG；
5. 不做随机裁剪、水平翻转、颜色增强或测试时几何变化。

若任一源图尺寸不是 1280×720、无法解码、不是有限像素或输出不是 256×256 RGB，整个构建失败，不得跳过该图后继续凑数。

### 4.4 运行时布局与不可覆盖规则

新的运行时根目录固定为：

`D:\DDM4IP-runtime\synthetic-benchmarks\bdd100k-motionblur-v1`

建议结构：

```text
bdd100k-motionblur-v1/
  status.json
  build.log
  source-manifest.csv
  split-manifest.csv
  summary.json
  preprocessing.json
  degradation/
    kernel-gt.pt
    kernel-gt.png
    degradation.json
  step1-observation/
    noisy/
  step2-clean/
    clean/
  test-paired/
    clean/
    noisy/
    pairs.jsonl
  dev-reserve/
    clean/
```

目标根目录已存在时，构建器必须拒绝执行；不得先删除、覆盖或混合旧文件。所有派生图像、清单、核和配置均需记录 SHA-256。原始数据和现有硬链接视图只读，不得修改。

## 5. 已知真实退化的定义

### 5.1 真实核

第一版只使用论文 FFHQ motion-blur 配置：

```text
kind        = motion_blur
kernel_size = 32
intensity   = 0.5
rnd_seed    = 1
noise_std   = 0.02
```

`ddm4ip/degradations/motion_blur.py` 已在 Windows/Pillow 环境中修复 32×32 核线宽为 0 导致全零核和 NaN 的问题。构建时必须实际生成一次 `k_gt`，验证：

- 形状与配置一致；
- 所有值有限且非负；
- 核和在数值容差内等于 1；
- 不是全零、delta 或无法解释的异常核；
- 保存张量、可视化、生成参数和 SHA-256。

后续所有 Step 1、测试集和 Oracle 必须加载同一份已冻结 `kernel-gt.pt`，不得各自重新随机生成“相同名称”的核。

### 5.2 模糊与噪声

合成观测定义为：

`y = clamp(A_k_gt(x) + epsilon, 0, 1)`，其中 `epsilon ~ N(0, 0.02^2 I)`。

实现必须复用 `instantiate_single_kernel()` 创建的项目 `Blur` 物理算子，固定 `padding="replicate"`、项目当前 kernel 方向、逐 RGB 通道相同核和 same-size 输出；不得另写一套 SciPy/Pillow 卷积替代。输出必须与清晰图同为 3×256×256。测试噪声按样本固定：每个 `test_paired` 行保存唯一 `noise_seed`，重复构建或评估必须得到相同像素与哈希。

Step 1 的 1,000 张观测也作为固定数据集生成和保存，使恢复、断点续训及跨对话验证不依赖 DataLoader 的随机调用次序。该做法相对论文在线退化实现可能减少噪声重采样，但保持“固定未知核下的一组退化观测”这一研究协议，并换取可审计、可重放的数据输入；必须在最终报告中列为实现差异。

## 6. 三阶段训练与评估数据流

### 6.1 Step 1：学习退化观测分布

- 唯一输入为 `step1-observation/noisy`；
- Batch 中不得携带对应源清晰图供损失、绘图或验证使用；
- 使用与论文 FFHQ 相同级别的 256×256 小型 flow 基线，训练预算在实施计划中以官方配置为起点；
- 只验证 flow 训练、检查点和观测分布建模链路，不计算恢复 PSNR、SSIM、LPIPS。

### 6.2 Step 2：从独立清晰分布学习核

- 唯一清晰输入为 `step2-clean/clean`；
- 输入图与 Step 1、正式测试集完全不重叠；
- 加载经独立 SHA-256 和内部 global step 核验的 Step 1 最终 checkpoint；
- 真实核 `k_gt` 不进入优化，只在 Step 2 完成后的只读核误差分析中使用；
- 正式设计以 5 个 Step 2 随机种子为目标，并固定同一个 Step 1 checkpoint，与论文报告随机性的方法一致；
- 8 GB GPU 上是否能在一个阶段窗口内完成 5 个种子，必须先由 pilot 实测速率和显存后决定，不能静默削减训练预算或种子数。

### 6.3 Step 3：成对定量恢复

`test-paired` 的每一行必须包含同一源图产生的：

- `clean_path`：清晰真值；
- `noisy_path`：由固定 `k_gt` 和固定噪声生成的观测；
- `source_id`、源/派生 SHA-256；
- `noise_seed`、输入输出尺寸和预处理记录。

评估数据集必须通过清单显式配对，不能只依赖两个目录排序或文件数量相等。文件缺失、ID 不同、尺寸不同、重复 `source_id`、哈希不符或目标输出已存在时必须拒绝运行。

## 7. 三组恢复结果与指标定义

每个正式测试样本必须产生三组比较：

1. `input`：模糊观测 `y` 与清晰真值 `x_gt`；
2. `oracle`：使用真实核 `k_gt` 和固定非盲求解器恢复；
3. `learned`：使用 Step 2 学到的 `k_hat` 和同一个非盲求解器恢复。

Oracle 与 learned 必须使用完全相同的求解器、先验权重、噪声水平、迭代参数、输入图和指标实现；两者唯一允许变化的是核。不得分别调参。

正式图像指标冻结为：

- PSNR：RGB、范围 `[0,1]`、逐图计算、整张 256×256 图，无事后边缘裁剪；
- SSIM：RGB、`data_range=1`、`channel_axis=0`、逐图计算；
- LPIPS：AlexNet 版本、输入 `[0,1]` 并由现有封装使用 `normalize=True`、逐图计算；
- 所有恢复输出先按项目现有路径 clamp 到 `[0,1]`。

还需报告 `k_hat` 对 `k_gt` 的 kernel PSNR 和 kernel NCC；核形状不同时只能使用项目已有、明确记录的对齐规则，不能手工挑选偏移使结果更好。

每张图写入 `metrics.jsonl`，至少包括：实验 ID、Step 2 seed、source ID、clean/noisy/prediction 路径和 SHA-256、真实核/估计核 SHA-256、PSNR、SSIM、LPIPS、输入输出尺寸、求解器配置哈希。汇总文件至少包括样本数、均值、标准差、中位数、最小值、最大值和失败数。

论文 FFHQ Table 2 的原始主指标是 PSNR、LPIPS；本实验按用户要求增加 SSIM，并明确标为本项目的附加主指标。由于数据域不同，不使用论文的 28.8 dB/0.069 作为通过阈值。

## 8. 代码与配置边界

预计新增而不是覆盖以下能力，具体文件名可在实施计划中根据现有结构微调：

1. `scripts/build_bdd100k_synthetic_benchmark.py`：冻结源清单、划分、预处理、真实核和成对测试集；
2. 新的 synthetic 数据集配置：分别表达 Step 1 noisy-only、Step 2 clean-only、Step 3 manifest-paired；
3. `step1_bdd100k_synthetic.yaml`、`step2_bdd100k_synthetic.yaml`、`step3_bdd100k_oracle.yaml`、`step3_bdd100k_synthetic.yaml`；
4. manifest-paired 数据加载契约及完整溯源元数据；
5. 每图指标记录器和确定性聚合器；
6. 运行器 spec 对 synthetic 主线、Oracle 和 5 个 Step 2 seeds 的明确支持。

现有 `ddm4ip/utils/metrics.py` 和 `DeepInvLoss.compute_img_metrics()` 已具备 PSNR、SSIM、LPIPS 计算能力。实施时优先复用并补齐标量化、逐图记录、聚合和版本冻结，不为了“看起来改动大”而重写指标数学公式。

现有真实 BDD100K 配置、no-reference 测试、全图几何、输出清单和禁止伪配对的契约必须继续通过。

## 9. 测试与验收门

### 9.1 无训练测试

实施必须采用测试先行，至少覆盖：

- 1,739 个源 ID 被精确分为 1,000/100/500/139，集合交集为空；
- 构建器在目标存在、源数量变化、SHA 不符、异常尺寸或重复 ID 时拒绝写入；
- 中央裁剪和 bicubic 缩放坐标、尺寸固定；
- `k_gt` 有限、非负、归一化且哈希稳定；
- 测试 clean/noisy 一一对应且重复加载逐像素一致；
- Step 1 batch 不向训练损失暴露清晰真值；
- Step 2 不读取正式测试图，不把 `k_gt` 用作优化目标；
- 人工相同图的 PSNR/SSIM/LPIPS 达到各自理想值，受控扰动后的方向正确；
- 指标逐图记录和总体聚合可由独立计算复核；
- BDD100K 真实 noisy-only 路线仍不输出伪 PSNR、SSIM、LPIPS；
- Hydra 四个新实验配置均能通过实际模块入口解析。

### 9.2 数据构建验收

构建数据属于远端数据处理，必须在用户单独授权的新对话中通过 Windows 任务计划程序执行。完成后在新的 SSH 会话中独立验证状态、退出码、文件计数、清单哈希、抽样像素、配对关系、核哈希和磁盘位置。后台状态为 `SUCCESS` 不能替代独立验证。

### 9.3 Oracle 门

在任何长训练前，先用 `dev_reserve` 中固定的小样本完成真实核 Oracle GPU pilot，确认：

- 求解器权重已提前落在 D 盘项目缓存，首次下载不混入 pilot；
- 输入、输出、真值尺寸完全一致；
- 三项指标均为有限值；
- Oracle 相比模糊输入的总体 PSNR/SSIM 上升、LPIPS 下降；
- 每图文件、清单、日志和状态均可追溯。

若 Oracle 无法改善输入，停止在评估链路，不允许继续用长训练掩盖问题。

### 9.4 训练与正式评估门

每一阶段必须先 pilot、后完整运行，并在新对话中单独授权。Step 2 只能接收独立核验的 Step 1 checkpoint；Step 3 只能接收独立核验的 Step 2 snapshot。正式测试集在实现冻结、Oracle 门和所有训练完成前不得用于选择超参数。

## 10. 长任务、目录和状态

所有数据生成、pilot、训练和正式评估均在 `group-pc` 上由 Windows 任务计划程序托管。项目 Python 固定为 `E:\Anaconda3\envs\ddm4ip\python.exe`；进程级 TEMP、TMP、PIP_CACHE_DIR、TORCH_HOME、XDG_CACHE_HOME 等继续指向 `D:\DDM4IP-runtime` 的项目专用子目录，不修改全局环境。

实验根目录建议固定为：

`D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1`

每个阶段保留追加式日志、`RUNNING/SUCCESS/FAILED` 状态、实际命令、解析配置、输入清单哈希、checkpoint、输出和指标。助手启动后只做一次任务/进程/日志更新确认，不在对话中持续轮询；必须向用户提供状态查看和 `Get-Content -Tail 50 -Wait` 日志命令。

## 11. 阶段拆分与授权边界

后续工作按新对话拆分，旧对话中的批准不自动授权下一阶段：

1. **设计审核：** 用户审核本文；不写实施计划、不改代码；
2. **实施计划：** 用户明确批准本文后，使用 `writing-plans` 生成逐文件、测试先行的实施计划；不实施；
3. **代码与无训练测试：** 实现数据构建器、配置、配对加载、指标记录和运行器支持，只运行无训练单元/配置测试；
4. **数据构建：** 单独授权计划任务生成 synthetic benchmark，并独立验收；
5. **Oracle GPU pilot：** 单独授权，验证真实核恢复和指标链路；
6. **Step 1 pilot/full：** 分别授权并验收最终 checkpoint；
7. **Step 2 pilot/full：** 固定 Step 1，先测一个 seed，再按预算运行 5 seeds；
8. **Step 3 正式评估：** 先 Oracle 全集，再逐 seed learned 全集；
9. **结果复盘：** 独立复算指标、检查失败样本并撰写有边界的结论。

任何阶段失败时停在该阶段，不自动开始下一个阶段。`prepare`、夹具和故意失败任务均不是训练或学习产物。

## 12. 成功标准与结论边界

完成标准是：

1. 500 对正式测试 clean/noisy 有明确共同 source ID、固定退化和完整哈希；
2. input、oracle、learned 三组每图 PSNR、SSIM、LPIPS 均可独立复算；
3. Oracle 使用真实核，learned 使用经验证的估计核，除核外配置相同；
4. Step 1/2 训练从未使用测试真值或配对监督；
5. 5 个 Step 2 seed 的产物、指标和随机性均有记录，或在预算限制下由用户明确批准减少并标为偏差；
6. 真实 BDD100K no-reference 主线没有被覆盖或错误升级为有真值实验；
7. 最终报告区分“任务成功运行”“Oracle 链路有效”“学习核准确”“恢复质量改善”四种不同结论。

本设计保证指标的定义和真值关系合法，不保证模型一定达到某个预设数值。若 learned 没有超过 input，必须如实报告并定位核估计、域统计或求解器原因，不能更换测试样本、删除失败图或用测试集调参来制造好结果。

## 13. 已知风险

- BDD100K 道路图与 FFHQ 人脸的数据分布不同，不能用论文数值作为硬阈值；
- 当前没有视频/来源 ID，无法完全排除相似道路帧跨集合泄漏；
- 中央正方形裁剪会舍弃左右视野，这是与全分辨率真实路线不同的明确设计选择；
- 固定保存 Step 1 噪声实现与官方在线噪声可能不同，但更容易审计和重放；
- 8 GB GPU 可能要求减小评估 batch size；任何可能改变优化统计的训练 batch/累积步数修改都需单独论证；
- README 与部分官方配置的 checkpoint 编号存在不一致，不能按相似名称自动选择；
- 远端当前工作树已有大量用户修改，任何实现必须逐文件避让并保存现有改动；
- 远端工作树中的 `WORKLOG.md` 当前不存在且 Git 状态为 `AD`。在用户明确处理前，不得擅自恢复或覆盖；跨对话恢复暂以本文和本机控制目录 `AGENTS.md` 为入口。

## 14. 新对话恢复协议

下一次对话首先完整读取本机 `AGENTS.md` 和 `WORKLOG.md`，连接 `group-pc`，核验主机名为 `DESKTOP-KBM1345`，检查远端 Git 状态和远端 `WORKLOG.md` 是否仍缺失，然后完整阅读本文。不得因为看到了设计批准就推定已经获准生成数据、训练或评估。

用户审核本文后，可在新对话粘贴：

> 我已审核并批准远端 `D:\Unsupervised Imaging Inverse Problems\docs\superpowers\specs\2026-09-06-bdd100k-known-blur-quantitative-reproduction-design.md`。请先按 AGENTS.md 完成启动核验，再使用 writing-plans 为该设计编写逐文件、测试先行的实施计划。本对话只授权写计划，不授权修改代码、生成数据、启动 pilot、训练、评估或计划任务。

实施计划审核通过后，再为“代码与无训练测试”单独开新对话并只授权该阶段。这样每个新对话都能从稳定文件恢复事实，同时不会误用上一阶段的授权。
