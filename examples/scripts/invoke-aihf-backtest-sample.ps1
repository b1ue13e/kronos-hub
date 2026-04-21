param(
    [string]$BaseUrl = "http://127.0.0.1:8010"
)

. (Join-Path $PSScriptRoot "hub-common.ps1")
Import-KronosHubEnv

$openAiKey = Get-RequiredEnvValue -Name "OPENAI_API_KEY"
$financialKey = Get-RequiredEnvValue -Name "FINANCIAL_DATASETS_API_KEY"

$body = @{
    tickers = @("AAPL")
    start_date = "2024-06-03"
    end_date = "2024-06-10"
    initial_capital = 100000.0
    margin_requirement = 0.0
    selected_analysts = @("technical_analyst", "fundamentals_analyst")
    model_name = "gpt-5.4"
    model_provider = "OpenAI"
    portfolio_positions = @()
    api_keys = @{
        OPENAI_API_KEY = $openAiKey
        FINANCIAL_DATASETS_API_KEY = $financialKey
    }
    environment = New-NoProxyEnvironment
}

Invoke-KronosHubJsonRequest -Endpoint "/execution/ai-hedge-fund/backtest" -Body $body -BaseUrl $BaseUrl
