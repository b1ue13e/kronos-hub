# Development Guide

本文档面向准备继续开发 `Kronos Hub` 的维护者和贡献者。

## 设计原则

开发这个仓库时，建议始终遵循这三个原则：

1. `integration-first`
   先保证三个项目能被稳定调度，再考虑更深的融合。
2. `thin hub, thick boundary`
   Hub 负责契约、调度和包装，不轻易在根项目里复制上游业务逻辑。
3. `prefer isolation`
   尽量保留上游项目独立运行的能力，不为了“一体化”把环境和依赖揉碎。

## 本地开发准备

### 1. 子项目目录

默认目录结构：

```text
repo-root/
├─ ai-hedge-fund-main/
├─ TradingAgents-main/
├─ Kronos-master/
└─ kronos_hub/ ...
```

如果你的目录不同，请在 `.env` 中配置：

- `KRONOS_HUB_AI_HEDGE_FUND_PATH`
- `KRONOS_HUB_TRADINGAGENTS_PATH`
- `KRONOS_HUB_KRONOS_PATH`

### 2. 虚拟环境建议

推荐准备四个环境：

- `.venv-hub`
- `.venv-aihf`
- `.venv-tradingagents`
- `.venv-kronos`

其中：

- `.venv-hub` 只装 Hub 自己的依赖
- 三个子项目各装各自依赖

然后在 `.env` 中配置：

- `KRONOS_HUB_AI_HEDGE_FUND_PYTHON`
- `KRONOS_HUB_TRADINGAGENTS_PYTHON`
- `KRONOS_HUB_KRONOS_PYTHON`

### 3. 安装 Hub 依赖

```powershell
pip install -e .
```

或者：

```powershell
.\scripts\bootstrap_hub.ps1
```

## 常用命令

### 自检

```powershell
python .\scripts\smoke_check.py
```

### 单元测试

```powershell
python -m unittest
```

### 启动 API

```powershell
.\scripts\run_api.ps1
```

或：

```powershell
python -m uvicorn apps.api_gateway.main:app --reload --port 8010
```

### 运行示例脚本

```powershell
.\examples\scripts\invoke-kronos-sample.ps1
.\examples\scripts\invoke-tradingagents-sample.ps1
.\examples\scripts\invoke-aihf-run-sample.ps1
.\examples\scripts\invoke-aihf-backtest-sample.ps1
```

## 模块职责建议

### 修改 `kronos_hub.api`

适用于：

- 新增路由
- 调整请求模型
- 修改 API 层异常处理

不建议：

- 在这里塞入大量业务逻辑

### 修改 `kronos_hub.services`

适用于：

- 新增 worker payload 字段
- 整理参数映射
- 统一默认值

不建议：

- 在这里复制上游项目的核心算法

### 修改 `kronos_hub.workers`

适用于：

- 进入真实子项目执行逻辑
- 处理上游项目导入路径
- 标准化返回结构

注意：

- worker 是 Hub 和上游项目之间最敏感的边界层
- 修改这里时，最好同步补充示例请求和测试

### 修改 `kronos_hub.engines`

适用于：

- 新增引擎适配器
- 扩展 `hybrid` 编排能力
- 调整 dry-run / planned / completed 响应语义

## 扩展一个新引擎时建议遵循的步骤

1. 在 `kronos_hub/engines/adapters/` 添加新 adapter。
2. 在 `kronos_hub/services/` 增加服务层封装。
3. 在 `kronos_hub/workers/` 增加 worker。
4. 在 `EngineRegistry` 中注册新引擎。
5. 在 `kronos_hub/api/routers/` 增加路由或复用 `/runs`。
6. 更新 `docs/api.md`、`README.md` 和示例请求。
7. 补充最小测试。

## 提交代码前的最小检查

至少执行：

```powershell
python .\scripts\smoke_check.py
python -m unittest
```

如果你修改了：

- API 路由：请至少手动验证一条真实请求
- worker：请至少跑通对应 `examples/scripts/*.ps1`
- `.env.example` / README：请确认文档步骤和实际命令一致

## 关于 vendored 子项目

当前仓库直接包含上游项目目录，这带来两个现实约束：

1. 不要轻易把大量上游源码改成只适配当前 Hub 的形态。
2. 修改上游目录时，最好在 PR 描述中说明：
   - 为什么必须改
   - 改动是否可能回灌上游
   - 是否影响第三方许可证和后续同步

更理想的长期方案可能是：

- submodule
- subtree
- 或拆成独立服务部署

## 当前最值得推进的开发方向

### `hybrid` 真实串联

- 定义 `Kronos` 输出到 `TradingAgents` 输入的共享 schema
- 把 forecast 信号注入研究流程
- 把研究结论转为可执行 / 可回测输入

### 统一结果模型

- 统一预测结果
- 统一研究报告摘要
- 统一执行 / 回测输出
- 为未来前端或数据库存储打基础

### 统一产品边界

- 明确 Hub 是否是最终后端
- 决定 `ai-hedge-fund` 前端是复用、改造还是替换
- 决定上游项目在仓库中的长期组织方式
