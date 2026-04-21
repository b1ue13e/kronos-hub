param(
    [string]$BaseUrl = "http://127.0.0.1:8010",
    [string]$CsvPath = "F:\kronos\Kronos-master\tests\data\regression_input.csv",
    [int]$Lookback = 64,
    [int]$PredLen = 8,
    [string]$ModelId = "NeoQuasar/Kronos-mini",
    [string]$TokenizerId = "NeoQuasar/Kronos-Tokenizer-2k"
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
    history = $history
    pred_len = $PredLen
    future_timestamps = $futureTimestamps
    model_id = $ModelId
    tokenizer_id = $TokenizerId
    max_context = 256
    temperature = 1.0
    top_k = 0
    top_p = 0.9
    sample_count = 1
    verbose = $false
    environment = New-NoProxyEnvironment
}

Invoke-KronosHubJsonRequest -Endpoint "/predictions/kronos" -Body $body -BaseUrl $BaseUrl
