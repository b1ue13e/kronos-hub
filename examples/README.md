# Example Requests

This folder contains runnable examples for calling the hub gateway directly.

## Layout

- `requests/`
  JSON request templates
- `scripts/`
  PowerShell invocation scripts

## Runnable without external API keys

### Kronos forecast

```powershell
.\examples\scripts\invoke-kronos-sample.ps1
```

This sample reads:

- [regression_input.csv](F:/kronos/Kronos-master/tests/data/regression_input.csv)

And calls:

- `POST /predictions/kronos`

### Hybrid demo chain

```powershell
.\examples\scripts\invoke-hybrid-demo.ps1
```

This calls:

- `POST /runs`

With:

- `engine = hybrid`
- a real Kronos forecast request
- hub-side signal synthesis
- optional expansion flags for research and execution

## Requires API keys

### TradingAgents research

```powershell
.\examples\scripts\invoke-tradingagents-sample.ps1
```

Required:

- `OPENAI_API_KEY`

### AI Hedge Fund run

```powershell
.\examples\scripts\invoke-aihf-run-sample.ps1
```

Required:

- `OPENAI_API_KEY`
- `FINANCIAL_DATASETS_API_KEY`

### AI Hedge Fund backtest

```powershell
.\examples\scripts\invoke-aihf-backtest-sample.ps1
```

Required:

- `OPENAI_API_KEY`
- `FINANCIAL_DATASETS_API_KEY`

### AI Hedge Fund style comparisons

Run multiple dual-analyst samples:

```powershell
.\examples\scripts\invoke-aihf-style-compare.ps1
```

Backtest multiple styles:

```powershell
.\examples\scripts\invoke-aihf-style-backtests.ps1
```

Covered styles:

- growth: `NVDA`, `technical_analyst + growth_analyst`
- ETF: `QQQ`, `technical_analyst + sentiment_analyst`
- China ADR: `BABA`, `technical_analyst + sentiment_analyst`

## Notes

These scripts load the root [`.env`](F:/kronos/.env) first, then fall back to the current environment for API keys.

If you only want the minimal hybrid demo, `invoke-hybrid-demo.ps1` can run with forecast-only settings. `-EnableResearch` and `-EnableExecution` expand the chain and will usually require external API keys.
