# Contributing

欢迎继续完善 `Kronos Hub`。

这个仓库的重点不是重写三个上游项目，而是把它们以更稳的方式组织成一个可继续演进的平台。因此，贡献时请优先保护好边界、契约和可验证性。

## 先看这几个文件

- `README.md`
- `docs/architecture.md`
- `docs/api.md`
- `docs/development.md`
- `THIRD_PARTY_NOTICES.md`

## 推荐的本地开发流程

1. 准备 `.env`
2. 安装 Hub 依赖
3. 配置三个子项目的独立解释器
4. 运行 smoke check
5. 再开始改代码

常用命令：

```powershell
Copy-Item .env.example .env
pip install -e .
python .\scripts\smoke_check.py
python -m unittest
.\scripts\run_api.ps1
```

## 提交前最低要求

如果你的改动要合并，请至少保证：

- `python .\scripts\smoke_check.py` 可以通过
- `python -m unittest` 可以通过
- README / docs / 示例请求与实际行为一致

如果你修改了 worker 或 API，请尽量再做一次手动调用验证。

## 代码组织约定

### 在 Hub 中新增能力时

优先修改这些层：

- `kronos_hub/api`
- `kronos_hub/services`
- `kronos_hub/workers`
- `kronos_hub/engines`

不要把大量上游业务逻辑直接复制到 Hub。

### 在上游目录中改代码时

请先问自己三个问题：

1. 这个改动是否真的必须发生在上游目录？
2. 这个改动是否会让将来的上游同步更难？
3. 这个改动是否会影响第三方许可证或归属说明？

如果答案不清晰，优先考虑在 Hub 侧做适配。

## 文档要求

下列改动通常需要同步更新文档：

- 新增路由
- 修改请求体字段
- 修改示例脚本
- 新增环境变量
- 新增引擎或扩展 `hybrid`

至少同步更新：

- `README.md`
- `docs/api.md`
- `docs/development.md`

## 测试建议

当前仓库以轻量测试为主，主要覆盖：

- 引擎注册表
- service payload 拼装

如果你新增行为，建议至少补一种：

- 一个 unit test
- 一个示例请求模板
- 一个最小手动验证脚本

## PR 说明建议

建议在 PR 描述中写清楚：

- 你解决了什么问题
- 影响哪些层
- 是否改动了上游 vendored 目录
- 如何验证
- 是否需要额外环境变量或 API key

## 风格建议

- Hub 代码尽量保持薄、清晰、可追踪
- 配置项和默认值尽量集中
- 对外返回结构尽量稳定
- 优先修正边界和契约，再追求“优雅抽象”
