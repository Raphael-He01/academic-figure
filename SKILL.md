---
name: academic-figure
description: Create, revise, and verify scientific figures using reproducible R in RStudio or editable Origin projects. Use for statistical plots including effect-size, forest and survival plots, benchmark comparisons, spatial maps, forecast and decision diagnostics, heatmaps, multi-panel figures, mechanism schematics, exports, legends, Results prose, and learning reusable figure-design rules from user references or public journal figures, including dsh-assisted discovery. Also use for graphical abstracts, AI-assisted schematic planning and audits, optional APA figure formatting, and LaTeX inclusion of finished figures. Also use to browse, select, recall or save named scientific colour cards.
---

# Academic Figure

从研究问题和可核对的记录出发，为论文、报告或建模项目制作可编辑、可复核的图稿。根据用户要拿到的成品和已有项目自动选择入口。组合任务可分别处理，例如先从参考图提取“按样本 ID 对齐”的规则，再用用户自己的表制作图谱。

## 先按交付物进入

| 用户需要 | 从哪里开始 | 何时交付 |
|---|---|---|
| 新图或一套图 | 从下面的第 1 步开始，先读数据和已有分析 | 最终尺寸的图已导出，关键图元与数据已核对，随附可编辑源、图注和验收范围 |
| 修订旧图 | 找到对应图稿、源文件、配置、原数据版本及用户指定的改动 | 重绘受影响图稿，复核改变的科学含义、呈现和实际导出 |
| 审核已有图稿 | 直接检查送审文件，按所给材料选择可验层级 | 按文件说明问题、位置与证据；不可验的层级标记 `NOT AUDITABLE`。用户要求修复时进入修订 |
| 学习参考图 | 先索引全部指定图片与图注，从已有来源记录续读；每张按八项维度记录可见、文述、建议与未知 | 写出数据适用条件、为何选这种编码及其局限，并用一个正例和一个缺失关键输入的反例检验迁移规则。[逐图学习](references/reference-learning-protocol.md) · [来源与历次记录](references/sources.md) |
| 浏览、选择或保存配色 | 用中文名、ID 或 HEX 查找色卡。新组合填写名称、来源、角色和候选状态 | 提供色卡与调用方式。已要求用于本套图时，一并记入第 6 步。[色卡用法](references/palette-library.md) · [离线色卡](assets/palettes/catalog.html) |
| 修改工作流或偏好 | 备份受影响入口，查找调用它的指南、配置、脚本或模板 | 更新对应入口，并按改动范围验证链接、命令或产物；注明个人设置或发行版的适用范围 |

## 首次运行或更换环境

首次制图、重绘或运行示例时，先记住原任务、数据、应用与已选色卡。在 skill 根目录执行 `python3 scripts/check_environment.py --route rstudio --json`；已指定 Origin 或命令行演示时分别用 `origin`、`rscript`。再在实际项目 R 会话检查所需包及项目库。仅看色卡、参考图或已有文件时，按任务直接使用对应工具。

缺少软件或配置时，按当前系统和项目定位缺项。用户已授权安装时，对选定 R 路线使用同一命令加 `--install-missing` 或按平台使用官方安装器，再恢复实际项目依赖并复检；需要系统认证时请用户在原生提示框完成。环境就绪后沿用已确定的路线、项目与色卡，继续原制图任务并验收导出。具体命令、官方安装入口和失败后的续作见[首次配置](references/first-run.md)。

## 使用范围

公开试用版默认在 RStudio 执行保存的 R 代码。当前用户选择 Origin 且现有许可和运行环境可用时，可直接制作和核验原生图。只选择能满足本次精度、可编辑性与复现要求的路线。分工制图时记录每个文件的生成应用及最终主文件。Rscript 可执行回归或模拟演示，记录为命令行实测。账户、付费、安装或新建虚拟机的操作以当前用户授权为准。[RStudio](references/r-workflow.md) · [Origin](references/origin-handoff.md)

公开参考发现可选用 dsh 整理公开元数据、候选与必要截图，由主代理核对原图和图注。私人图稿、论文和数据留在本地。用户提供的截图可以支持设计观察，声称特定期刊、科学数值或原始色值时需另有依据。[辅助检索与核验](references/assisted-journal-learning.md)

公开版的安装、依赖和实测范围见[使用说明](README.md)。历史记录提供设计理由，本次操作以当前用户、任务和授权为准。

## 制作一套图的十步

1. **圈定本次交付。** 识别新建、修订、审核或续作，确定 figure set 的范围、各图用途和最终载体。能从需求和项目读出的事项直接沿用。
2. **查明数据能回答什么。** 先确认一行代表谁、原始来源与版本，再核对单位、样本 ID、连接、分母、缺测、配对、筛选和变换。缺一个面板的证据时，标出具体缺口并继续独立面板。CSV 可用工具预检，再从数据字典和方法确认字段含义。[数据检查与选图](references/data-and-chart-selection.md)
3. **写下五点图稿契约。** 在项目已有说明中一次记录 *Question and supported claim*（问题及可支持的结论）、*Evidence roles*（各面板证据）、*Composition*（布局）、*Data and inference boundary*（数据与推断边界）、*Destination and export agreement*（尺寸与交付）。记录剔除及原因。探索性任务可将结论留作 `missing`；只向用户核实会改变科学解释或交付的歧义。[五点契约](references/figure-contract.md)
4. **选图型与制作工具。** 按问题检索 V01–V32，比较所需数据和一个有意义的替代方案。在已核实的事实表可用时，可运行 `python3 scripts/figure_routes.py V04 --facts facts.json` 联查对应首选图的条件；其余按索引人工核对。用本页所列授权范围选 RStudio 或 Origin，保留决定理由。只有各期边际总数时画构成；有可追溯的相邻阶段转移量时可画流向。[32 类图型](references/figure-family-index.md) · [模型输出实例](references/model-output-routing.md) · [证据检查](scripts/chart_guard.py)
5. **准备可重绘的项目。** 优先使用已有项目、依赖、字典和冻结的分析结果。新 R 项目可用 `python3 scripts/scaffold_project.py <新目录>` 建立；Origin 建立数据链接并保留原始工作簿。用稳定 ID 连接表，处理代码与样式分开保存。脚手架自带的示例数据保留模拟身份。[R 项目模板](scripts/scaffold_project.py)
6. **整套图只选一次色卡。** 先读该套图的已有决定。用户已指定、已确认或明确委托时直接采用并记录；尚未决定时展示 2–3 套适用色卡，优先推荐雾海玫瑰（`rose_mist`），等待用户选择再作依赖配色的渲染。等待时可继续独立核数。将套图范围、色卡 ID、版本和具名组别到色值的映射保存在现有配置；后续图、补图和续作共用这项决定。在 R 中固定整套图的有序组名，各图传入 `figure_config(palette_id = set_card, groups = figure_groups, set_groups = set_groups)`，按组名复用颜色、点形与线型。类别多于主色时优先用点形、线型、直接标签或分面。连续量的方向、中点和缺测色按其含义另定。[色卡选择](references/palette-system.md)
7. **按最终尺寸定版。** 指定共用坐标、类别顺序、单位与颜色角色，设定字体、标记大小、面板间距和输出设备。简约、清爽、浅暖的填色搭配可辨认的深色文字和关键线条。没有投稿目标时，89/183 mm 栏宽和 7–8 pt 正文仅作暂定起点。已有目标时核对当前投稿阶段的官方要求并记录来源和日期。[期刊要求](references/journal-requirements.md) · [多面板布局](references/multipanel-evidence-architecture.md)
8. **先看最难读的一幅，再完成整套。** 在选定应用执行保存的代码或原生图，先用预定尺寸查看最密集、最易被误读的面板，再检查其余面板及合图。决定是否需要同源放大、直接标注或拆面板，并记录选点依据。位置、面积、明度和线宽各自对应明确变量。复核所有可能改变结论的失败个案和缺测状态。
9. **在最终文件上验收。** 分别检查科学映射、面板几何、文件与字体、最终尺寸的目检。按键复算关键值及分母，用灰度与色觉模拟检查实际标记。把实测、失败、待查与不适用分开写入现有记录。对齐规则、1.5 PDF pt 容差、局部例外和每轮修复上限均以此指南为准。重导出后复验新文件并检查最终组图。[成图核验](references/rendered-qa.md)
10. **对齐图、文字和文件版本。** 按用户语言交付，默认中文图题、图注与 Results。对图中单位、样本数、区间和限制逐项对账，缺少的图注信息标记 `[待补充]`。用同一图号关联预览、请求的矢量/位图、可编辑源及配置、来源/数据字典、依赖与执行记录。用已有导出清单保留格式、尺寸、版本、文件摘要、适用 QA 与有依据的结论，并说明遗留事项。[图注与结果](references/caption-and-results.md) · [验收与溯源字段](references/rendered-qa.md#extend-the-existing-export-manifest)

## 批量、修订与续作

- **批量制图**。将套图共用的数据版本、组别映射、投放宽度和已选色卡写一次。每张图记录自己的问题、图型、样本范围、比较基准和证据状态。相同问题保留可直接比较的尺度；不同问题可以分别展示总体、分布或失败个案。先用一个风险较高的面板验证共享设置，再用于其余图。逐图核对各自的数据与实际导出。
- **只改一处**。只改图外图注，且图文件摘要相同时，复核图文一致性；图内标签或投放尺寸改变，从排版开始并验新文件；换色卡，更新套图绑定及受影响图例，检查同组在各图中的实际颜色；分母、筛选或分析版本改变，则回到第 2 步，重核依赖它的图元、图注及结论。[修订的复核范围](references/rendered-qa.md#reuse-evidence-only-within-its-revision-scope)
- **收到“继续”**。从现有项目记录恢复套图范围、输入/输出版本、上次实测、已选色卡和未决事项；核对它们仍对应的文件，从首个未完成或因改动而失效的步骤接续。记录中缺少信息时先从项目、配置和清单恢复，确实无法恢复的项标为待核对。

## 按需查阅

- 绘图方法从[数据与图型对照](references/data-and-chart-selection.md)进入。有多种模态和证据角色时查[多面板结构](references/multipanel-evidence-architecture.md)；有真实样本编号或动态加权样本时，分别查[样本图谱](references/sample-atlas.md)或[状态概率场](references/weighted-state-fields.md)。
- 机制示意先查[可编辑矢量流程](references/vector-schematic-workflow.md)和[对象与箭头](references/vector-schematic-style-rules.md)，逐条核对关系证据。图文摘要或 AI 辅助规划另查[适用范围](references/ai-graphical-abstract-workflow.md)。
- Nature 与 NMI 按目标和提交阶段查看[版式差异](references/nature-flagship-and-nmi-requirements.md)。指定 APA 格式时使用[APA 约定](references/apa-figure-profile.md)，已有成图需放入论文时使用[LaTeX 插图](references/latex-inclusion.md)。
