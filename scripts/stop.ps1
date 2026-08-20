$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot; $docker = Join-Path $env:LOCALAPPDATA "Programs\DockerDesktop\resources\bin\docker.exe"; if (-not (Test-Path $docker)) { $docker="docker" }
Push-Location $root; try { & $docker compose stop } finally { Pop-Location }
