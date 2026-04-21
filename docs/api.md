# API Reference

本文档说明 `Kronos Hub` 当前已经暴露的主要接口、用途和样例来源。

## Base URL

默认本地地址：

```text
http://127.0.0.1:8010
```

Swagger 文档：

```text
http://127.0.0.1:8010/docs
```

## 公开路由概览

| Method | Path | 说明 |
| --- | --- | --- |
| `GET` | `/` | 根信息，返回名称、版本、host、port 和 docs 路径 |
| `GET` | `/health` | Hub 健康状态 |
| `GET` | `/engines` | 所有引擎描述 |
| `GET` | `/engines/{engine_name}` | 单个引擎详情 |
| `GET` | `/projects` | 子项目发现状态与入口文件提示 |
| `POST` | `/runs` | 通用引擎调用入口 |
| `POST` | `/predictions/kronos` | Kronos 单序列预测 |
| `POST` | `/predictions/kronos/batch` | Kronos 批量预测 |
| `POST` | `/research/tradingagents` | TradingAgents 研究流程 |
| `POST` | `/execution/ai-hedge-fund/run` | AI Hedge Fund 执行 / 分析流程 |
| `POST` | `/execution/ai-hedge-fund/backtest` | AI Hedge Fund 回测流程 |

---

## `GET /health`

返回 Hub 整体状态，包括：

- `status`
- `engine_count`
- `available_engine_count`
- `subproject_count`

适合用于：

- 启动后烟雾测试
- 监控或本地调试

---

## `GET /engines`

返回所有引擎的说明信息：

- 名称与展示名
- 描述
- capabilities
- project_root
- available

当前引擎：

- `kronos`
- `tradingagents`
- `ai_hedge_fund`
- `hybrid`

---

## `GET /projects`

返回三个子项目的发现状态：

- `key`
- `path`
- `exists`
- `entrypoints`
- `notes`

适合在启动前快速确认：

- 目录是否存在
- 路径覆盖是否生效
- Hub 是否找到了正确的上游项目目录

---

## `POST /runs`

统一引擎调用入口，适合以后接前端或调度系统时复用。

基础请求体字段：

- `engine`
- `tickers`
- `start_date`
- `end_date`
- `trade_date`
- `dry_run`
- `api_keys`
- `environment`
- `options`

说明：

- 当 `dry_run=true` 时，适配器通常返回计划信息或建议命令
- 当 `dry_run=false` 时，适配器会进入真实 worker 调用

适用引擎：

- `kronos`
- `tradingagents`
- `ai_hedge_fund`
- `hybrid`

---

## `POST /predictions/kronos`

执行单序列 OHLCV 预测。

请求体核心字段：

- `history`: OHLCV 记录数组
- `pred_len`: 预测长度

常用可选字段：

- `future_timestamps`
- `model_id`
- `tokenizer_id`
- `max_context`
- `device`
- `temperature`
- `top_k`
- `top_p`
- `sample_count`
- `environment`

示例模板：

- [`examples/requests/kronos.predict.template.json`](../examples/requests/kronos.predict.template.json)

示例脚本：

- [`examples/scripts/invoke-kronos-sample.ps1`](../examples/scripts/invoke-kronos-sample.ps1)

---

## `POST /predictions/kronos/batch`

执行批量预测。

与单序列预测相比，关键差异是：

- 使用 `series` 数组
- 每个元素可带自己的 `history`
- 每个元素可带自己的 `future_timestamps`

适合：

- 对多资产或多样本做统一推理
- 在同一模型配置下批量生成未来 OHLCV

---

## `POST /research/tradingagents`

执行多代理研究与决策流程。

请求体核心字段：

- `ticker`
- `trade_date`

常用可选字段：

- `selected_analysts`
- `llm_provider`
- `deep_think_llm`
- `quick_think_llm`
- `max_debate_rounds`
- `max_risk_discuss_rounds`
- `output_language`
- `backend_url`
- `data_vendors`
- `tool_vendors`
- `debug`
- `config_overrides`
- `api_keys`
- `environment`

典型返回内容：

- `decision`
- `reports.market_report`
- `reports.sentiment_report`
- `reports.news_report`
- `reports.fundamentals_report`
- `reports.investment_plan`
- `reports.final_trade_decision`

示例模板：

- [`examples/requests/tradingagents.research.openai.template.json`](../examples/requests/tradingagents.research.openai.template.json)

示例脚本：

- [`examples/scripts/invoke-tradingagents-sample.ps1`](../examples/scripts/invoke-tradingagents-sample.ps1)

依赖说明：

- 通常需要模型供应商 API key
- OpenAI 场景下可能还会读取 `OPENAI_API_BASE` 或 `OPENAI_BASE_URL`

---

## `POST /execution/ai-hedge-fund/run`

执行 AI Hedge Fund 的分析 / 执行流程。

请求体核心字段：

- `tickers`

常用可选字段：

- `start_date`
- `end_date`
- `initial_cash`
- `margin_requirement`
- `selected_analysts`
- `model_name`
- `model_provider`
- `show_reasoning`
- `portfolio_positions`
- `api_keys`
- `environment`

示例模板：

- [`examples/requests/aihf.run.openai.template.json`](../examples/requests/aihf.run.openai.template.json)
- [`examples/requests/aihf.run.style-growth-nvda.template.json`](../examples/requests/aihf.run.style-growth-nvda.template.json)
- [`examples/requests/aihf.run.style-etf-qqq.template.json`](../examples/requests/aihf.run.style-etf-qqq.template.json)
- [`examples/requests/aihf.run.style-china-baba.template.json`](../examples/requests/aihf.run.style-china-baba.template.json)

示例脚本：

- [`examples/scripts/invoke-aihf-run-sample.ps1`](../examples/scripts/invoke-aihf-run-sample.ps1)
- [`examples/scripts/invoke-aihf-style-compare.ps1`](../examples/scripts/invoke-aihf-style-compare.ps1)

---

## `POST /execution/ai-hedge-fund/backtest`

执行回测流程。

请求体核心字段：

- `tickers`
- `start_date`
- `end_date`

常用可选字段：

- `initial_capital`
- `margin_requirement`
- `selected_analysts`
- `model_name`
- `model_provider`
- `portfolio_positions`
- `api_keys`
- `environment`

典型返回内容：

- `performance_metrics`
- `portfolio_values`
- `final_portfolio_value`

示例模板：

- [`examples/requests/aihf.backtest.openai.template.json`](../examples/requests/aihf.backtest.openai.template.json)

示例脚本：

- [`examples/scripts/invoke-aihf-backtest-sample.ps1`](../examples/scripts/invoke-aihf-backtest-sample.ps1)
- [`examples/scripts/invoke-aihf-style-backtests.ps1`](../examples/scripts/invoke-aihf-style-backtests.ps1)

---

## 常见错误来源

### 1. 子项目路径未找到

排查：

- 检查 `KRONOS_HUB_*_PATH`
- 检查根目录下子项目目录名称是否正确
- 调用 `/projects` 查看发现结果

### 2. 解释器依赖不完整

排查：

- 检查 `KRONOS_HUB_*_PYTHON` 是否指向正确环境
- 为三个子项目分别安装各自依赖
- 先跑 `python .\scripts\smoke_check.py`

### 3. API key 缺失

排查：

- 检查 `.env`
- 检查请求体中的 `api_keys`
- 检查上游项目自身的 `.env` 加载逻辑

### 4. Worker 返回 500

排查：

- 响应体通常会包含 `stdout` / `stderr`
- 可以直接运行 `examples/scripts/*.ps1` 验证最小链路
- 先从单个引擎跑通，再考虑 `hybrid`
