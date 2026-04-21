param(
    [string]$Host = "127.0.0.1",
    [int]$Port = 8010
)

$root = Split-Path -Parent $PSScriptRoot
$currentPythonPath = $env:PYTHONPATH
$hubPython = Join-Path $root ".venv-hub\Scripts\python.exe"

if ([string]::IsNullOrWhiteSpace($currentPythonPath)) {
    $env:PYTHONPATH = $root
} else {
    $env:PYTHONPATH = "$root;$currentPythonPath"
}

$env:HTTP_PROXY = ""
$env:HTTPS_PROXY = ""
$env:http_proxy = ""
$env:https_proxy = ""
$env:ALL_PROXY = ""
$env:all_proxy = ""
$env:NO_PROXY = "*"
$env:no_proxy = "*"

Set-Location $root
if (Test-Path $hubPython) {
    & $hubPython -m uvicorn apps.api_gateway.main:app --host $Host --port $Port --reload
} else {
    python -m uvicorn apps.api_gateway.main:app --host $Host --port $Port --reload
}
