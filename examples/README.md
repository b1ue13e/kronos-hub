# Example Requests

这里放的是给 hub 网关直接调用的示例。

## 文件结构

- `requests/`
  - JSON 模板，请求结构一眼能看懂
- `scripts/`
  - PowerShell 一键调用脚本

## 直接可跑

### Kronos 预测

```powershell
.\examples\scripts\invoke-kronos-sample.ps1
```

默认会读取：

- [regression_input.csv](F:/kronos/Kronos-master/tests/data/regression_input.csv)

并调用：

- `POST /predictions/kronos`

## 需要 API key

### TradingAgents 研究

```powershell
.\examples\scripts\invoke-tradingagents-sample.ps1
```

需要：

- `OPENAI_API_KEY`

### AI Hedge Fund 执行

```powershell
.\examples\scripts\invoke-aihf-run-sample.ps1
```

需要：

- `OPENAI_API_KEY`
- `FINANCIAL_DATASETS_API_KEY`

### AI Hedge Fund 回测

```powershell
.\examples\scripts\invoke-aihf-backtest-sample.ps1
```

需要：

- `OPENAI_API_KEY`
- `FINANCIAL_DATASETS_API_KEY`

### AI Hedge Fund 风格对比

运行多组双 analyst 样例：

```powershell
.\examples\scripts\invoke-aihf-style-compare.ps1
```

回测多组风格：

```powershell
.\examples\scripts\invoke-aihf-style-backtests.ps1
```

覆盖风格：

- 成长股：`NVDA`，`technical_analyst + growth_analyst`
- ETF：`QQQ`，`technical_analyst + sentiment_analyst`
- 中概股：`BABA`，`technical_analyst + sentiment_analyst`

## 说明

这些脚本会优先加载根目录的 [`.env`](F:/kronos/.env)，再从当前环境变量读取 API key。
