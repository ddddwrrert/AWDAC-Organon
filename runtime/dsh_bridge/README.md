# AWDAC-Organon

这是 Organon 的外围增强工程。原版目录位于项目根目录的 `Organon_original/`。构建器读取原版 Worker 变异函数，把它与 AWDAC 上下文合成 DSH 的动态插件。插件只注册 `mutate`，并把候选分配、Worker 启动及失败处理交回原版函数。原版一次分配消耗 1 Budget，初始候选消耗 0 Budget。每个增强候选沿用同一次 Worker Session 和正式评价。

| 文件 | 职责 |
| --- | --- |
| `awdac/capability.js` | Worker 在已有任务中阅读实际 Parent 源码，识别机制、依赖和替代方案 |
| `awdac/regression.js` | 根据已记录的裁决和原版 merit 标记退化，缺失证据时保留未知 |
| `awdac/collaboration.js` | 提示独立判断、反驳和自主选择实现方案 |
| `awdac/evidence.js` | 读取同一运行的父子评估，匹配条件一致的逐 Seed 结果 |
| `awdac/provider.js` | 组装上下文后调用原版变异函数 |
| `experiments/profiles.json` | 原版、三个单项消融和完整版本的开关 |
| `scripts/build.mjs`、`scripts/report.mjs` | 生成 DSH 插件源码、生成运行报告 |
| `tests/framework.test.mjs` | 使用真实原版函数和测试运行环境验证接口、预算调用及报告 |

## 运行

需要 Node.js 20+。在项目目录运行：

```powershell
npm test
node scripts/build.mjs ../../../Organon_original full | Set-Content -Encoding utf8 awdac-host.txt
node scripts/report.mjs '<任务目录>/run' '<task.json 中的 program>'
```

在配置好的 DSH Evolve Mode 会话中，先检查 `evolve` 服务、可用 JS 内置对象和当前 provider 栈。把生成的文本作为 `evolve_define` 的 `host_code`，再用返回的插件 ID 调用 `evolve_activate`。确认 `mutate` 显示为 `awdac-worker-context`，再按原版方式调用 `evolve_run`。命令参数和部署方式以对应 DSH 版本的工具说明为准。切换消融使用独立会话和独立任务副本。基线直接运行原版。停用这个插件即可退回 provider 栈的下一层。原版若后续替换了 `mutate`，以 `evolve_plugins` 显示的栈顶为准，本实现不会自动包裹任意策略。

Agent 可读取报告或现有评价，按需通过已配置的文件工具把简短建议放入当前任务的 `run/awdac/agent-advice.txt`。建议会提供给该运行后续 Worker，更新方向时可覆盖或移除。Worker 将异议写入现有回复。异议没有独立审批或自动结构化持久化。HDPE、M9 和搜索算子设计均可在已有 Session 中按需使用。

## 数据和验收

原版评价文件为 `run/evals/<candidate>.json`，主字段为 `fitness` 和 `metrics`。诊断使用明确的 `judge_result`，未知或零分而无裁决的情况保留未知。接受状态下的分数下降只说明本次观测退化，具体算法机制与因果关系仍需实验确认。

所查的原版 ALE-Bench 评价只持久化汇总。若已有外部评估记录同一条件下的逐 Seed 原始分，可在外部报告副本的评价记录上附加 `awdac: {condition, direction, seeds}`。condition 必须由数据提供方编码实际任务、评价器版本、配置和实验条件，direction 为 min 或 max，seeds 为 Seed ID 到数值分数的映射。扩展字段由 AWDAC 定义，原版无需改动。没有配对数据时报告给出空列表。

报告输出原版候选目录计数、完成数、已接受且源码内容不同的子候选数、失败诊断和最佳 fitness。有效次数 N 是有明确接受裁决且可读取源码时的观测值。Q 使用明确接受的父子 merit 差。F 用评价文件、可判定状态和可配对 Seed 的覆盖情况表征，属于反馈覆盖指标。

验证时固定题目、初始代码、模型、Token 上限、评价条件及 100 次候选分配额度，使用重复运行比较基线与各增强配置。在日志中标记完全重写，并于实验前定义大崩及突破阈值。对比最终得分、随预算的表现、完全重写大崩率、突破率、Q、N 和 F。正式 DSH 激活、真实模型执行、Token 公平性和性能收益需要在实际环境验收。
