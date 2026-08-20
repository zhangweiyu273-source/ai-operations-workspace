$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot; $docker = Join-Path $env:LOCALAPPDATA "Programs\DockerDesktop\resources\bin\docker.exe"; if (-not (Test-Path $docker)) { $docker="docker" }
Push-Location $root; try { & $docker compose ps; Invoke-RestMethod "http://localhost:8000/api/v1/health/ready" | ConvertTo-Json } finally { Pop-Location }
