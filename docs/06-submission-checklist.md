# 最终交付清单

- 题目：企业知识问答 Agent；正式题号待提交者确认。
- GitHub URL：https://github.com/oylei/Enterprise-Knowledge-QA-Agent 。
- 最终 commit SHA：本地提交完成后运行 `git rev-parse HEAD` 获取；为避免提交自引用，不把同一提交的 SHA 写入自身。
- 私有仓库评审账号权限：待配置（如适用）。
- 实际投入时间：待据实填写。
- 个人修改、验证和学习收获：待补充到 04/05 文档。

代码、资料、离线测试、真实输入输出和 Trace、五份规定文档及 .env.example 已存在。未完成项详见 03-evaluation.md。

建议评审顺序：README → 03-evaluation → 真实 Trace → core.py → tests。运行命令以 README 为准。用户已提供目标仓库并授权交付；Git 远端读取及 HTTPS 连通性检查均超时，尚未完成推送。仓库内容将先保留本地提交；网络恢复后执行 `git push -u origin main`，若远端非空应先 fetch/review，不可强推。

提交时不包含 .env、真实密钥、.DS_Store、缓存。模型凭证只在本地填写，已出现在聊天中的凭证应在平台撤销轮换。
