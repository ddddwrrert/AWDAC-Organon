# AHC015 正式接入

| 环节 | 实现 |
| --- | --- |
| 默认 Worker 启动 | 原版 mutate 分配候选并调用原版 Worker。AWDAC 补充现有证据和自主改写提示 |
| Worker 回传 | 原有回复里的可选 AWDAC_INTENT 行，按候选写入 run/awdac/intents/ |
| 逐 Seed 导出 | 工作任务副本把同一次原版 50 Seed 评价的有效分数附加到 metrics.awdac，沿用 combined_score |
| Python 证据导入 | sync-ahc015 将既有评价和 Worker 意图关联保存到 SQLite，输出供同一 Agent Session 读取的上下文 |
| Agent 回传建议 | Agent 在已有轮次读取上下文，可通过 run/awdac/agent-advice.txt 向后续 Worker 提供可选建议 |

## 从 ZIP 启动

1. 在 Linux 按原版 README 配置 DSH、Docker、评测依赖及模型凭据。进入解压后的项目根目录。
2. 用下列命令创建一个全新的工作任务目录并生成桥接。原版目录保留为审计快照。

```bash
python -B -m scripts.run_awdac prepare-ahc015 "$PWD/ahc015-work"
node runtime/dsh_bridge/scripts/build.mjs Organon_original full > awdac-host.js
```

3. 在 ahc015-work 中开启原版 Evolve Mode。按桥接 README 使用 evolve_define 和 evolve_activate 加载生成的 host code，再确认 mutate 名为 awdac-worker-context。在同一 Session 按原版 PROMPT.md 运行。
4. 批次完成后从工程根目录同步证据。把输出交给同一 Agent 的下一轮作为事实材料，Agent 可写入可选建议。该步骤目前由操作者在批次间执行。

```bash
python -B -m scripts.run_awdac sync-ahc015 "$PWD/ahc015-work" --db "$PWD/ahc015-evidence.sqlite" > ahc015-context.json
```

正式缓存替代关闭。动态策略仍由 Organon 管理。若 Agent 激活其他 mutate provider，AWDAC 对默认 mutate 的包装会失去优先级。真实 DSH 与 Docker 评测尚未在当前机器运行。C++ 能力画像仍需要解析器。
