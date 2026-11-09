# 测试预期、实际结果与限制

正式评审入口：[examples/README.md](../examples/README.md)。以下23组均有真实输入、实际输出、Trace和元信息，覆盖正常、资料不足、工具失败以及所选题全部验收点。另有五类场景各三次重复测试。

| 用例 | 预期状态 | 实际状态 | 运行记录 |
|---|---|---|---|
| 01_正常回答_国内住宿限额 | answered | answered | [说明、输入、输出及Trace](../examples/验收用例/01_正常回答_国内住宿限额/说明.md) |
| 02_正常回答_境外住宿限额 | answered | answered | [说明、输入、输出及Trace](../examples/验收用例/02_正常回答_境外住宿限额/说明.md) |
| 03_适用范围_国内境外差异 | answered / needs_clarification | answered | [说明、输入、输出及Trace](../examples/验收用例/03_适用范围_国内境外差异/说明.md) |
| 04_文档冲突_期限冲突与口语改写 | conflict | conflict | [说明、输入、输出及Trace](../examples/验收用例/04_文档冲突_期限冲突与口语改写/说明.md) |
| 05_相似概念_付款时间与提交期限 | answered | answered | [说明、输入、输出及Trace](../examples/验收用例/05_相似概念_付款时间与提交期限/说明.md) |
| 06_相似概念_预借款结清 | answered | answered | [说明、输入、输出及Trace](../examples/验收用例/06_相似概念_预借款结清/说明.md) |
| 07_资料不足_发票无法补开 | insufficient_evidence / partial | partial | [说明、输入、输出及Trace](../examples/验收用例/07_资料不足_发票无法补开/说明.md) |
| 08_明确替代_新版住宿标准 | answered | answered | [说明、输入、输出及Trace](../examples/验收用例/08_明确替代_新版住宿标准/说明.md) |
| 09_历史适用_旧版住宿标准 | answered | answered | [说明、输入、输出及Trace](../examples/验收用例/09_历史适用_旧版住宿标准/说明.md) |
| 10_文档冲突_同日相反规定 | conflict | conflict | [说明、输入、输出及Trace](../examples/验收用例/10_文档冲突_同日相反规定/说明.md) |
| 11_部分回答_商务舱资料缺失 | partial | partial | [说明、输入、输出及Trace](../examples/验收用例/11_部分回答_商务舱资料缺失/说明.md) |
| 12_上下文追问_那境外呢 | answered | answered | [说明、输入、输出及Trace](../examples/验收用例/12_上下文追问_那境外呢/说明.md) |
| 13_信息不足_追问缺少指代 | needs_clarification | needs_clarification | [说明、输入、输出及Trace](../examples/验收用例/13_信息不足_追问缺少指代/说明.md) |
| 14_资料外问题_明年涨薪 | insufficient_evidence | insufficient_evidence | [说明、输入、输出及Trace](../examples/验收用例/14_资料外问题_明年涨薪/说明.md) |
| 15_不可信指令_拒绝999天 | answered | answered | [说明、输入、输出及Trace](../examples/验收用例/15_不可信指令_拒绝999天/说明.md) |
| 16_材料要求_餐饮与住宿 | answered | answered | [说明、输入、输出及Trace](../examples/验收用例/16_材料要求_餐饮与住宿/说明.md) |
| 17_适用边界_通勤不属差旅 | answered | answered | [说明、输入、输出及Trace](../examples/验收用例/17_适用边界_通勤不属差旅/说明.md) |
| 18_金额边界_正好5000元 | answered | answered | [说明、输入、输出及Trace](../examples/验收用例/18_金额边界_正好5000元/说明.md) |
| 19_工具失败_持续读取异常 | tool_error | tool_error | [说明、输入、输出及Trace](../examples/验收用例/19_工具失败_持续读取异常/说明.md) |
| 20_执行上限_明确未完成 | incomplete | incomplete | [说明、输入、输出及Trace](../examples/验收用例/20_执行上限_明确未完成/说明.md) |
| 21_资料替换对照_原始30天 | answered | answered | [说明、输入、输出及Trace](../examples/验收用例/21_资料替换对照_原始30天/说明.md) |
| 22_资料替换对照_替换20天 | answered | answered | [说明、输入、输出及Trace](../examples/验收用例/22_资料替换对照_替换20天/说明.md) |
| 23_资料替换对照_新增15天冲突 | conflict | conflict | [说明、输入、输出及Trace](../examples/验收用例/23_资料替换对照_新增15天冲突/说明.md) |

## 测试与评估结果

- [离线测试原始输出](../examples/离线测试结果_30项.txt)：30项通过。
- [稳定性及33次机械检查汇总](../examples/archive/v4原始全量回归/metrics.json)：33/33机械通过，不能解读为无语义缺陷。
- [语义审查](../examples/archive/v4原始全量回归/review.json)：E16存在资料范围歧义，E17有非业务冗余措辞。
- [开发集检索](../examples/检索对照_开发集8问.json)：Recall@5 87.5%→100%；[独立问法](../examples/检索对照_独立集12问.json)：83.3%→75%，未证明泛化提升。
- [检索恢复审查](../examples/archive/检索恢复原始记录/review.json)：三项找回证据，但H08先肯定后保留，不能算语义通过。

## 失败和已知限制

v2曾在冲突下建议按15天办理，v3存在版本日期与生效日期混淆、历史补充引用问题；均保留原始记录，v4修正后重新全量回归。语义审查为AI辅助阅读，不是独立人工盲评。三次重复不足以证明生产稳定性。原文逐字校验不能自动证明语义支持性。

详见[最终验证报告](07-final-validation.md)和[历史迭代记录](08-evaluation-history.md)。使用Python标准库原生实现，未采用Agent框架，因此无框架版本依赖。
