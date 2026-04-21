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
        start_date = "2024-05-20"
        end_date = "2024-06-14"
        analysts = @("technical_analyst", "growth_analyst")
    },
    @{
        label = "ETF-QQQ"
        tickers = @("QQQ")
        start_date = "2024-06-03"
        end_date = "2024-06-14"
        analysts = @("technical_analyst", "sentiment_analyst")
    },
    @{
        label = "China-BABA"
        tickers = @("BABA")
        start_date = "2024-05-20"
        end_date = "2024-06-14"
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
            initial_cash = 100000.0
            margin_requirement = 0.0
            selected_analysts = $case.analysts
            model_name = "gpt-5.4"
            model_provider = "OpenAI"
            show_reasoning = $false
            portfolio_positions = @()
            api_keys = @{
                OPENAI_API_KEY = $openAiKey
                FINANCIAL_DATASETS_API_KEY = $financialKey
            }
            environment = New-NoProxyEnvironment
        }

        $response = Invoke-RestMethod -Method Post -Uri "$BaseUrl/execution/ai-hedge-fund/run" -ContentType "application/json" -Body ($body | ConvertTo-Json -Depth 30)
        $ticker = $case.tickers[0]
        $decision = $response.result.decisions.$ticker

        $results += [pscustomobject]@{
            Style = $case.label
            Ticker = $ticker
            Analysts = ($case.analysts -join ", ")
            Action = $decision.action
            Quantity = $decision.quantity
            Confidence = $decision.confidence
            Reasoning = $decision.reasoning
        }
    } catch {
        $results += [pscustomobject]@{
            Style = $case.label
            Ticker = $case.tickers[0]
            Analysts = ($case.analysts -join ", ")
            Action = "ERROR"
            Quantity = 0
            Confidence = 0
            Reasoning = $_.Exception.Message
        }
    }
}

$results | Format-Table -AutoSize
