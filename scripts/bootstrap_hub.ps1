param(
    [string]$VenvPath = ".venv-hub"
)

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

python -m venv $VenvPath

$activate = Join-Path $root "$VenvPath\\Scripts\\Activate.ps1"
& $activate

$env:HTTP_PROXY = ""
$env:HTTPS_PROXY = ""
$env:http_proxy = ""
$env:https_proxy = ""
$env:ALL_PROXY = ""
$env:all_proxy = ""
$env:NO_PROXY = "*"
$env:no_proxy = "*"

python -m pip install --upgrade pip
python -m pip install -e .

Write-Host ""
Write-Host "Bootstrap complete."
Write-Host "Activate with: $activate"
Write-Host "Run API with: python -m uvicorn apps.api_gateway.main:app --reload --port 8010"
