# AWDAC-Organon

GitHub 克隆时使用 `git clone --recurse-submodules https://github.com/ddddwrrert/AWDAC-Organon.git` 获取固定版本的 Organon 原版。已克隆时运行 `git submodule update --init --recursive`。

Python 3.11+。项目包含可执行的参考后端、SQLite 证据库和 Organon 运行产物只读适配。参考后端以离线小型求解任务验证数据流。在线 DSH 会话接入状态见 [源码审计与验收](docs/original_audit.md)。

## 运行

在工程根目录执行。

```powershell
python -B -m awdac demo --db demo.sqlite
python -B -m awdac ablate
python -B -m unittest discover -s tests -v
python -B -m awdac inspect-original '<已有任务目录>'
python -B -m awdac inspect-original '<已有任务目录>' --parent c000000
```

可复制 `awdac/default.toml`，通过 `demo --config path.toml` 调整参考预算、Seed、诊断阈值和模块开关。`ablate` 为全开、全关、逐项启用提供独立内存数据库。参考 Worker 使用确定性的示例策略，因此这些结果只检查机制行为和计费，无法衡量真实模型的创新收益。

参考运行包含一次免费基线和三个计费候选分配。重复候选仍计分配额度。全新数据库首次运行会执行两次评价、复用两次原样结果，实际计算 8 个 Seed。另用已有数据库运行可能增加命中。每次报告含运行 ID，可在 SQLite 中按该 ID 查明细。

```sql
SELECT candidate, parent, json_extract(record, '$.paired.mean_delta')
FROM experiments WHERE run_id = '<run_id>' ORDER BY candidate;

SELECT kind, candidate, record FROM knowledge WHERE run_id = '<run_id>';
```

## 工程结构

| 文件 | 职责 |
| --- | --- |
| `awdac/schemas.py` | 评价条件、逐 Seed 数据、独立建议、Worker 修改意图 |
| `awdac/acu/` | Python AST 能力画像、函数调用依赖和组件对比 |
| `awdac/evidence/` | 条件一致性、配对差异、描述性不确定性、E1–E6、ECA |
| `awdac/learning.py` | M9/M7、算子假设、参考算子生成及归因记录 |
| `awdac/enhancer.py` | 形成上下文及反馈。候选分配和存活由后端拥有 |
| `awdac/memory/`、`schema.sql` | 按运行与候选保存谱系、知识、上下文检索和严格缓存 |
| `awdac/reference.py` | 参考 Agent、参考 Worker、求解器、评价，以及演示的后端选择规则 |
| `awdac/integration/organon_adapter.py` | 源码核对过的文件读取、预算统计和可交付给现有 Worker 的上下文 |
| `awdac/default.toml`、`cli.py`、`__main__.py` | 配置、CLI、运行与消融 |
| `tests/` | 单元、只读文件集成、CLI 端到端 |
| `docs/original_audit.md` | 源码审计、实时接入说明和验收矩阵 |

参考后端直接执行工程内部生成的 Python 示例。自定义 Worker 应使用受信任代码，真实候选执行应由原版运行环境处理。SQLite `experiments` 保持事实记录，`knowledge` 保持程序、算法和上下文反例，`evaluations` 只按内容及完整条件复用成功评价。源码、运行参数、环境、评价器、协议、Seed 顺序或正式/诊断用途变化都会造成缓存未命中。生产复用还需由环境方确认评价确定性、候选全部输入和环境指纹的完整性。

## 原版与验收

`Organon_original/` 由 Git 子模块固定到验收使用的原版提交。运行时应使用独立的任务副本，保留此快照供审计。

```powershell
python -B -m scripts.check_integrity
node runtime/dsh_bridge/scripts/build.mjs Organon_original full | Set-Content -Encoding utf8 awdac-host.js
```

生成的 host 代码用于默认 mutate 的 DSH 桥接。AHC015 的任务准备、回传与证据导入见 [接口映射与运行步骤](docs/integration_map.md)。在线操作和卸载方式见 [桥接说明](runtime/dsh_bridge/README.md)。

- [逐文件验收矩阵](docs/implementation_matrix.md)
- [测试报告及未完成事项](docs/test_report.md)
- [源码接入审计](docs/original_audit.md)


## 按验收目录运行

```powershell
python -B -m scripts.check_integrity
python -B -m scripts.audit_original
python -B -m scripts.run_awdac --config configs/awdac.yaml --db runtime/memory/demo.sqlite
python -B -m scripts.run_ablation --config configs/awdac.yaml
python -B -m scripts.run_original '<已有任务目录>'
python -B -m scripts.generate_report '<已有任务目录>'
```

`run_original` 读取已有原版运行产物。原版正式运行入口及环境设置见 `Organon_original/README.md`。四个 YAML 配置采用 JSON 兼容的 YAML 子集，内置加载器无需额外依赖。
