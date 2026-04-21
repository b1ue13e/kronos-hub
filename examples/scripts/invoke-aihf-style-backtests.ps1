param(
    [string]$BaseUrl = "http://127.0.0.1:8010"
)

. (Join-Path $PSScriptRoot "hub-common.ps1")
Import-KronosHubEnv

$openAiKey = Get-RequiredEnvValue -Name "OPENAI_API_KEY"
$financialKey = Get-RequiredEnvValue -Name "FINANCIAL_DATASETS_API_KEY"

$cases = @(
    @{
        label = "Growth-NVDA"
        tickers = @("NVDA")
        start_date = "2024-06-03"
        end_date = "2024-06-10"
        analysts = @("technical_analyst", "growth_analyst")
    },
    @{
        label = "ETF-QQQ"
        tickers = @("QQQ")
        start_date = "2024-06-03"
        end_date = "2024-06-10"
        analysts = @("technical_analyst", "sentiment_analyst")
    },
    @{
        label = "China-BABA"
        tickers = @("BABA")
        start_date = "2024-06-03"
        end_date = "2024-06-10"
        analysts = @("technical_analyst", "sentiment_analyst")
    }
)

$results = @()

foreach ($case in $cases) {
    try {
        $body = @{
            tickers = $case.tickers
            start_date = $case.start_date
            end_date = $case.end_date
            initial_capital = 100000.0
            margin_requirement = 0.0
            selected_analysts = $case.analysts
            model_name = "gpt-5.4"
            model_provider = "OpenAI"
            portfolio_positions = @()
            api_keys = @{
                OPENAI_API_KEY = $openAiKey
                FINANCIAL_DATASETS_API_KEY = $financialKey
            }
            environment = New-NoProxyEnvironment
        }

        $response = Invoke-RestMethod -Method Post -Uri "$BaseUrl/execution/ai-hedge-fund/backtest" -ContentType "application/json" -Body ($body | ConvertTo-Json -Depth 30)

        $results += [pscustomobject]@{
            Style = $case.label
            Ticker = $case.tickers[0]
            Analysts = ($case.analysts -join ", ")
            FinalValue = [math]::Round([double]$response.final_portfolio_value, 2)
            Sharpe = if ($null -ne $response.performance_metrics.sharpe_ratio) { [math]::Round([double]$response.performance_metrics.sharpe_ratio, 4) } else { $null }
            MaxDrawdown = if ($null -ne $response.performance_metrics.max_drawdown) { [math]::Round([double]$response.performance_metrics.max_drawdown, 6) } else { $null }
        }
    } catch {
        $results += [pscustomobject]@{
            Style = $case.label
            Ticker = $case.tickers[0]
            Analysts = ($case.analysts -join ", ")
            FinalValue = $null
            Sharpe = $null
            MaxDrawdown = $null
        }
    }
}

$results | Format-Table -AutoSize
