# Kronos Hub 中文说明

[English README](README.md) · [在线文档](https://b1ue13e.github.io/kronos-hub/) · [架构](docs/architecture.md) · [API 参考](docs/api.md) · [开发指南](docs/development.md)

Kronos Hub 用一层 FastAPI 网关把三个依赖和产品边界各不相同的项目接到同一套接口：`Kronos-master/` 做 OHLCV 时间序列预测，`TradingAgents-main/` 做多代理研究，`ai-hedge-fund-main/` 做分析、执行和回测。Hub 不把三套运行时合并成单体，而是提供共享 API、引擎注册表和 JSON 子进程 Worker；每个 Worker 可以绑定自己的 Python 解释器，减少 LangGraph/LangChain 与 PyTorch/Hugging Face 依赖冲突。

这是一个面向工程集成、研究和教学的仓库，不构成投资建议。根目录集成层采用 Apache-2.0；随仓库分发的三个上游目录保留各自的许可证、版权与声明。

## 当前接口

| 方法与路径 | 用途 |
| --- | --- |
| `GET /` | 名称、版本、配置的 host/port 和文档路径 |
| `GET /health` | Hub 健康状态、引擎数与子项目数 |
| `GET /engines`、`GET /engines/{engine_name}` | 引擎描述与可用状态 |
| `GET /projects` | 三个子项目目录和入口文件的发现结果 |
| `POST /runs` | `kronos`、`tradingagents`、`ai_hedge_fund`、`hybrid` 的统一调用入口 |
| `POST /predictions/kronos`、`POST /predictions/kronos/batch` | 单序列与批量 OHLCV 预测 |
| `POST /research/tradingagents` | 按股票代码、日期、分析员和模型配置运行多代理研究 |
| `POST /execution/ai-hedge-fund/run`、`POST /execution/ai-hedge-fund/backtest` | AI Hedge Fund 分析与回测 |

`hybrid` 会用 `options.history` 运行真实 Kronos 预测，在 Hub 内生成结构化信号摘要，再按 `options.enable_research` 和 `options.enable_execution` 选择是否继续调用 TradingAgents 与 AI Hedge Fund。后续调用仍需要对应上游依赖和凭据。当前桥接以 Hub 侧信号摘要与提示词注入为主；更深的工具级融合、统一前端、结果存储和日志尚未完成。

`dry_run=true` 的请求返回计划或命令信息，不进入真实 Worker。Worker 执行失败时，HTTP 500 响应提供捕获到的 `stdout` 和 `stderr`，便于定位解释器路径、上游依赖和模型供应商配置问题。

## 安装与启动

Hub 自身需要 Python 3.10+；三个子项目分别安装各自依赖。在仓库根目录运行：

```powershell
Copy-Item .env.example .env
pip install -e .
python .\scripts\smoke_check.py
python -m unittest
python -m uvicorn apps.api_gateway.main:app --reload --port 8010
```

也可以用 `.\scripts\bootstrap_hub.ps1` 建立独立 Hub 环境，用 `.\scripts\run_api.ps1` 按 `.env` 中的 `KRONOS_HUB_HOST` 和 `KRONOS_HUB_PORT` 启动。Swagger 位于 <http://127.0.0.1:8010/docs>；`GET /projects` 可核对子项目路径是否被发现。

`.env.example` 列出可用配置：`KRONOS_HUB_*_PATH` 覆盖子项目目录，`KRONOS_HUB_*_PYTHON` 指向各自的解释器，`OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、`GOOGLE_API_KEY`、`ALPHA_VANTAGE_API_KEY`、`FINANCIAL_DATASETS_API_KEY` 等只在上游流程需要时填写。`HubSettings.from_env()` 加载 `.env`，但不覆盖已经存在的环境变量；不要把 `.env` 提交到仓库。

## 示例请求

网关启动后可按 [examples/README.md](examples/README.md) 与 [hybrid 模板](examples/requests/hybrid.demo.template.json) 调用：

```powershell
.\examples\scripts\invoke-kronos-sample.ps1
.\examples\scripts\invoke-hybrid-demo.ps1
.\examples\scripts\invoke-hybrid-demo.ps1 -EnableResearch
.\examples\scripts\invoke-hybrid-demo.ps1 -EnableResearch -EnableExecution
```

[API 参考](docs/api.md)列出每个路由的必填和可选字段。真实预测要求 Kronos 解释器安装模型依赖；研究与执行还要求上游模型或数据服务可用。

## 架构与目录

```text
客户端 / 脚本
  → apps.api_gateway.main（FastAPI）
  → kronos_hub.api.routers（请求校验）
  → kronos_hub.services 或 EngineRegistry / adapters
  → kronos_hub.workers（JSON 子进程边界）
  → Kronos-master / TradingAgents-main / ai-hedge-fund-main
```

`kronos_hub/api/` 放路由与请求模型，`kronos_hub/settings.py` 和 `shared/project_paths.py` 负责环境与子项目发现，`engines/` 放注册表与四个适配器，`services/` 整理 Worker 参数，`workers/` 处理进入真实子项目的边界。`tests/`、`scripts/smoke_check.py` 和 `examples/` 分别提供单元测试、自检与可运行请求。设计理由和新增引擎的步骤见 [架构](docs/architecture.md) 与 [开发指南](docs/development.md)。

## 检查、文档与边界

```powershell
python .\scripts\smoke_check.py
python -m unittest
```

新增引擎时同步更新适配器、服务、Worker、注册表、路由或 `/runs` 契约、示例请求与测试。[CONTRIBUTING.md](CONTRIBUTING.md) 是贡献说明，[SECURITY.md](SECURITY.md) 是安全报告说明，[MERGE_ASSESSMENT.md](MERGE_ASSESSMENT.md) 保留最初的集成方案。分发完整仓库前阅读 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)、[NOTICE](NOTICE) 和根目录 [LICENSE](LICENSE)，并保留上游目录的许可证。

当前明确未完成的包括：TradingAgents 工具级预测融合、AI Hedge Fund 完全以 Hub 为统一后端、共享结果模型、统一前端、日志与结果存储。[开发指南](docs/development.md)中的路线图描述的是后续方向，不是已交付功能。
