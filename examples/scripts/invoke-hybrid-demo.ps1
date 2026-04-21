param(
    [string]$BaseUrl = "http://127.0.0.1:8010",
    [string]$CsvPath = "F:\kronos\Kronos-master\tests\data\regression_input.csv",
    [string]$Ticker = "AAPL",
    [int]$Lookback = 64,
    [int]$PredLen = 8,
    [switch]$EnableResearch,
    [switch]$EnableExecution
)

. (Join-Path $PSScriptRoot "hub-common.ps1")
Import-KronosHubEnv

$rows = Import-Csv $CsvPath | Select-Object -First $Lookback
if (-not $rows -or $rows.Count -lt 4) {
    throw "Not enough rows loaded from $CsvPath"
}

$history = @()
foreach ($row in $rows) {
    $history += @{
        timestamp = $row.timestamps
        open = [double]$row.open
        high = [double]$row.high
        low = [double]$row.low
        close = [double]$row.close
        volume = [double]$row.volume
        amount = [double]$row.amount
    }
}

$lastTimestamp = [datetime]::Parse($rows[-1].timestamps)
$futureTimestamps = @()
for ($i = 1; $i -le $PredLen; $i++) {
    $futureTimestamps += $lastTimestamp.AddMinutes(5 * $i).ToString("yyyy-MM-dd HH:mm:ss")
}

$body = @{
    engine = "hybrid"
    tickers = @($Ticker)
    dry_run = $false
    options = @{
        history = $history
        pred_len = $PredLen
        future_timestamps = $futureTimestamps
        model_id = "NeoQuasar/Kronos-mini"
        tokenizer_id = "NeoQuasar/Kronos-Tokenizer-2k"
        max_context = 256
        temperature = 1.0
        top_k = 0
        top_p = 0.9
        sample_count = 1
        enable_research = [bool]$EnableResearch
        enable_execution = [bool]$EnableExecution
    }
}

if ($EnableResearch) {
    $body.trade_date = "2026-01-15"
    $body.options.llm_provider = "openai"
    $body.options.deep_think_llm = "gpt-4.1"
}

if ($EnableExecution) {
    $body.start_date = "2025-01-01"
    $body.end_date = "2025-03-01"
    $body.options.mode = "backtest"
    $body.options.model_name = "gpt-4.1"
    $body.options.model_provider = "OpenAI"
}

Invoke-KronosHubJsonRequest -Endpoint "/runs" -Body $body -BaseUrl $BaseUrl
