function Get-KronosHubRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

function Import-KronosHubEnv {
    $root = Get-KronosHubRoot
    $envPath = Join-Path $root ".env"
    if (-not (Test-Path $envPath)) {
        return
    }

    Get-Content $envPath | ForEach-Object {
        $line = $_.Trim()
        if (-not $line) { return }
        if ($line.StartsWith("#")) { return }
        $parts = $line -split "=", 2
        if ($parts.Count -ne 2) { return }
        $key = $parts[0].Trim()
        $value = $parts[1].Trim()
        if (-not [string]::IsNullOrWhiteSpace($key)) {
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

function Invoke-KronosHubJsonRequest {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Endpoint,

        [Parameter(Mandatory = $true)]
        [object]$Body,

        [string]$BaseUrl = "http://127.0.0.1:8010"
    )

    $json = $Body | ConvertTo-Json -Depth 30
    $response = Invoke-RestMethod -Method Post -Uri "$BaseUrl$Endpoint" -ContentType "application/json" -Body $json
    $response | ConvertTo-Json -Depth 30
}

function New-NoProxyEnvironment {
    return @{
        HTTP_PROXY = ""
        HTTPS_PROXY = ""
        ALL_PROXY = ""
        NO_PROXY = "*"
    }
}

function Get-RequiredEnvValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    $value = [Environment]::GetEnvironmentVariable($Name, "Process")
    if ([string]::IsNullOrWhiteSpace($value)) {
        throw "Missing required environment variable: $Name"
    }
    return $value
}
