# 原版源码审计

本文记录原版审计及早期适配状态。AHC015 的当前实现和操作步骤见 [接口映射](integration_map.md)。

审计对象为Organon 上游工作树，提交 `fcd1e501ee589d363766136aceb60527a0f06b12`。另核对了 本地历史运行产物、JS 接入参考、`OR-Operator/V3.0` 的机制说明和 `OR(seed2)` 的评价分支。它们各自的调度及评价扩展不能当作原版接口。实现以本轮附件和引用会话的取舍要求为依据。目录规格见逐文件矩阵。

## 接口审计

| 接口 | 源码位置与语义 | 本项目验收状态 |
| --- | --- | --- |
| Agent / DSH | `PROMPT.md`、`plugins/dsh-evolve-loop/presets/evolve.patch.yml`、`src/index.js`。Evolve Mode 主会话反复调用 `evolve_run`，在各批之间通过原版 provider 工具修改搜索策略 | 源码确认。在线建议写入现有 Session 的调用方待映射 |
| Worker | `src/providers/mutate.js` 分配一个候选，然后将指令交给 `src/evolve.js::spawnWorker`。该方法通过 DSH subagent 服务启动候选目录内的子会话。目录约束入口在 `plugins/dsh-candidate-builder/src/tool.ts` | 源码确认。Python 生成上下文已验证。在线注入、Worker 回复及 Token 导出待接入 |
| 预算 | `src/budget.js`、`src/candidates.js`、`src/evolve.js::allocate`。首次运行固定 cap，物理候选目录中序号大于零的目录计入 used。100 来自原版运行提示，计量对象为候选分配。未进入 population 的分配仍计费，基线免费 | 源码、测试夹具及真实历史产物已验证 |
| 种群 | `src/providers/loop.js` 按原版 select / mutate / evaluate / survive 调用。默认 Provider 的行结构见 `src/population.js`，`merit` 将负向 fitness 转成可比较的排序权重 | 只读原版行、parent、survival 已验证。参考选择规则仅用于玩具任务 |
| 评价 | `src/providers/evaluate.js` 调用 `run_evaluator.py`，读取各任务的 `task.json`，写入 `run/evals/<id>.json`，返回 fitness | 源码与真实历史汇总已验证。在线 evaluator hook 待接入 |
| 正式 Seed | 原版 `tasks/ale_bench/ahc015/evaluator/evaluator.py` 用 `case_gen(list(range(50)))`。成功时以方向因子乘 `overall_absolute_score / 50`，失败的最小化任务有特殊处理。产物只含整体评分、裁决与部分统计。OR(seed2) 另有 `OR_SEEDS` 配置 | AHC015 口径源码已确认。逐 Seed 常规导出待映射。其他任务沿其自身评价协议。 |
| 原版完整性 | 项目只读取原版目录及运行产物 | 测试夹具读前后 SHA-256 一致，真实原版审计前后 Git 工作树均干净。未运行原版在线回归套件 |

## 在线接入步骤

1. 使用原版 Evolve Mode 和独立任务副本。以完成的批次为快照运行 `inspect-original`。
2. 在已有 Agent 会话中读取快照并提出可选建议。通过受支持的动态 provider 接入时，用 `mutate(options, evolve)` 的 `instruction` 参数附加上下文，再调用当前匹配的原版变异实现。原版工作区已有独立 JS 桥接参考，其实现绑定默认 mutate。使用自定义 mutate 时应重新核对运行栈，避免覆盖策略。交付包含该桥接的副本，已在本地夹具测试，在线激活待验证。
3. 完成评价后继续读取原版行与汇总。已有逐 Seed 原始结果时，用来源确认后的任务与评价身份构造 `Condition` 和 `Seed`，再调用 `paired`，或将同条件的结果交给 `Enhancer.feedback`。历史汇总无法恢复逐 Seed 数据。AHC015 的求解文件是 C++，当前 Python AST 分析不会生成其组件画像，需接入 C++ 静态分析器或已有真实轨迹。
4. 在外部旁路保存 Worker 结构化意图、真实裁决和成本。真实运行缓存需要原版评价集成及公平性验证，当前线上评价沿原版运行。DSH 调用、动态 provider 激活、跨进程预算审计及真实消融需独立验收。

## 验收矩阵

| 能力 | 工程验证结果 | 仍需验收 |
| --- | --- | --- |
| A1 / ACU | 参考 Parent 与 Baseline 画像、调用依赖、函数改动及证据级别 | C++ 能力解析、真实运行迹线和受控实验标注 |
| A2 / HDPE / M1–M4 | 参考 Worker 生成完整新算子，测试覆盖组合。记录改动意图和关联评价 | 真实模型驱动的开放式生成、受控算子贡献验证 |
| A3 / Budget Reuse | 候选分配、基线豁免、完整缓存键、原版历史预算读取 | 原版缓存接入和线上 Token 账本 |
| A4 / Seed、M9/M7、ECA、CLR/CEL | 条件隔离、逐 Seed 配对、描述性标准误、差异和意图持久化、未知观察输入、方向性可靠度、同任务上下文召回 | 真实逐 Seed 导出、跨算法的可靠度校准、因果验证 |
| A5 / AWDAC | 参考 Agent 建议与 Worker 反驳同存，首轮 radical 改写 | 真实 Session 的双向结构化传递 |
| Regression | E1–E6 分类及未知裁决保留，依据明确状态判断 | 不同原版任务裁决和预算遥测映射 |
| 实验收益 | 离线单项开关及参考试跑，真实历史只读 | 原版完整回归、同预算多题多次消融、可重复 AHC 性能收益 |

本轮执行记录见 [测试报告](test_report.md)。
