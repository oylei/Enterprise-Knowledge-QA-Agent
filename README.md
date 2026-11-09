# 企业知识问答 Agent

Python 3.9+，标准库实现，无运行时第三方依赖。业务范围为合成差旅与报销制度。已完成 30 项离线测试和多轮完整真实模型回归；六类题目必验场景均有实际记录，已知问题和未完成项见评估文档。

## 快速运行

在仓库根目录执行，无需安装：

```sh
PYTHONPATH=src python3 -m enterprise_qa ask --question '报销需要哪些材料？'
PYTHONPATH=src python3 -m enterprise_qa ask --question '报销期限多久？' --dataset data/conflict.json
PYTHONPATH=src python3 -m enterprise_qa ask --question '报销材料' --fail-reads 99
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

默认使用 Mock，仅验证流程，不证明模型决策能力。输出及逐步 Trace 自动写入 examples/runs/。工具持续失败或未完成返回退出码 2；业务终态返回 0。

## DeepSeek

在项目根目录的 `.env` 中填写 DEEPSEEK_API_KEY 和 DEEPSEEK_MODEL；可选 DEEPSEEK_BASE_URL，默认 https://api.deepseek.com。CLI 自动读取当前目录的 `.env`，也可用 `--env-file 路径` 指定。已有 shell 环境变量优先。仅解析字面值，不执行 shell 命令、不展开变量；支持整行注释、export 前缀和成对引号，不支持行尾注释。错误信息不会包含配置值。

本地 `.env` 已被 Git 忽略；新克隆仓库可先执行 `cp .env.example .env`，不要将密钥提交仓库。模型名称使用账号当前支持工具调用的型号。

```sh
PYTHONPATH=src python3 -m enterprise_qa ask --provider deepseek --question '报销期限多久？' --dataset data/conflict.json
```

模型通过原生 Tool Calls 选择 search_documents、read_passage 和 finish，执行器回传实际结果。没有配置密钥或模型名称时明确报错，不自动降级伪装真实运行。

上下文输入使用 `--input 文件路径` 替代 `--question`，JSON 结构为 `{"question":"那需要交什么？","history":[{"role":"user","content":"我想了解差旅报销"}]}`。历史仅接受 user/assistant。真实模型负责上下文理解；Mock 没有实现上下文推理。

执行上限参数：`--max-turns 12 --max-calls 16`；每个动作含 finish 均计数。故障注入参数 `--fail-reads N` 表示前 N 次读取失败，仅用于测试。

## 评审入口

- docs/01-requirements.md：需求与验收矩阵。
- docs/02-solution.md：当前实现、动态决策和技术取舍。
- docs/03-evaluation.md：已运行结果及未完成项。
- examples/run-summary.json：四条实际离线运行结果。
- examples/runs/：对应输入、输出、元信息和 Trace。
- examples/test-results.txt：实际测试输出。

引用检查可防止引用未读取或不存在的文字，不能自动证明语义蕴含。已完成上述场景的单次真实模型验证与开发集检索对照，已补充五类核心场景各3次重复测试，样本量仍小。目标仓库为 https://github.com/oylei/Enterprise-Knowledge-QA-Agent ，发布状态见交付清单。

## 扩充资料与评估问题

资料说明见 [data/README.md](data/README.md)。`data/rich.json` 为丰富但无故意未消解冲突的资料；`data/rich_conflict.json` 加入期限冲突。另有适用范围、明确替代、同日非数字冲突、部分缺失和不可信指令快照。

[examples/evaluation-cases.json](examples/evaluation-cases.json) 包含 18 个评估输入与人工检查标准，尚不是实际输出。18项已全部执行真实模型验证，另有工具失败、上限与资料替换对照；机械检查不等于语义审查。

## 可选平台：硅基流动

在 `.env` 填写 `SILICONFLOW_API_KEY`（硅基流动平台签发）。默认 `SILICONFLOW_MODEL=deepseek-ai/DeepSeek-V3.2`，`SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1`。使用独立变量，避免将旧平台密钥误发给新平台。旧 DeepSeek 入口继续兼容，默认运行仍为离线 Mock。

```sh
PYTHONPATH=src python3 -m enterprise_qa ask --provider siliconflow --question '报销期限多久？' --dataset data/rich_conflict.json
```

官方接口说明：https://docs.siliconflow.cn/docs/api/chat-completions-post
模型与账号可用性需实际调用确认；曾进行在线尝试，但因余额不足未完成业务运行。

## 当前验证与提交入口

当前成功验证平台为 DeepSeek 官方，模型 `deepseek-v4-flash`。运行仍默认 Mock，真实调用必须显式传 `--provider deepseek`。

```sh
PYTHONPATH=src python3 -m enterprise_qa ask --provider deepseek --input examples/inputs/E12.json --dataset data/rich.json
PYTHONPATH=src python3 scripts/evaluate_retrieval.py
```

六类必验场景及实际文件映射见 [评估文档](docs/03-evaluation.md)。每个运行目录同时保存 input.json、final.json、trace.jsonl、metadata.json；Mock、真实模型、接口失败记录分开辨认，不应把接口失败计作模型效果。

提交前填写 [交付清单](docs/06-submission-checklist.md)。GitHub URL、题号、最终 commit SHA、实际用时及个人复盘尚需提交者补充。仓库运行不需要构建安装；Python 标准库零第三方运行依赖。pyproject.toml 的 setuptools 仅供可选打包，未锁定构建环境，不声称打包过程完全可复现。

## 完整验证命令

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 scripts/evaluate_retrieval.py
PYTHONPATH=src python3 scripts/evaluate_holdout.py
# 以下调用真实模型，会产生平台费用；输出目录可断点续跑，重测请换目录。
PYTHONPATH=src python3 scripts/evaluate_model.py --output examples/new-evaluation
python3 scripts/summarize_evaluation.py examples/new-evaluation
```

最新结论见 [最终验证报告](docs/07-final-validation.md)。独立检索集出现退步和模型语义问题都保留，不能把33项机械通过解读为33项无缺陷。默认重复集合覆盖明确答案、冲突、上下文、资料外和工具失败。
