param(
    [string]$BaseUrl = "http://127.0.0.1:8010",
    [string]$Ticker = "NVDA",
    [string]$TradeDate = "2024-05-10"
)

. (Join-Path $PSScriptRoot "hub-common.ps1")
Import-KronosHubEnv

$openAiKey = Get-RequiredEnvValue -Name "OPENAI_API_KEY"
$alphaVantageKey = Get-RequiredEnvValue -Name "ALPHA_VANTAGE_API_KEY"
$openAiBase = [Environment]::GetEnvironmentVariable("OPENAI_API_BASE", "Process")
if ([string]::IsNullOrWhiteSpace($openAiBase)) {
    $openAiBase = "https://api.openai.com/v1"
}

$body = @{
    ticker = $Ticker
    trade_date = $TradeDate
    selected_analysts = @("market")
    llm_provider = "openai"
    deep_think_llm = "gpt-5.4"
    quick_think_llm = "gpt-5.3-codex-spark"
    max_debate_rounds = 1
    max_risk_discuss_rounds = 1
    output_language = "Chinese"
    backend_url = $openAiBase
    data_vendors = @{
        core_stock_apis = "alpha_vantage,yfinance"
        technical_indicators = "alpha_vantage,yfinance"
        fundamental_data = "alpha_vantage,yfinance"
        news_data = "alpha_vantage,yfinance"
    }
    tool_vendors = @{}
    debug = $false
    config_overrides = @{
        connection_retry_attempts = 4
        connection_retry_base_delay = 2.0
    }
    api_keys = @{
        OPENAI_API_KEY = $openAiKey
        ALPHA_VANTAGE_API_KEY = $alphaVantageKey
    }
    environment = New-NoProxyEnvironment
}

Invoke-KronosHubJsonRequest -Endpoint "/research/tradingagents" -Body $body -BaseUrl $BaseUrl
