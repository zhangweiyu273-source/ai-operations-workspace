$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot; $docker = Join-Path $env:LOCALAPPDATA "Programs\DockerDesktop\resources\bin\docker.exe"; if (-not (Test-Path $docker)) { $docker="docker" }
Push-Location $root; try { & $docker compose up -d --build --force-recreate; & $docker compose ps } finally { Pop-Location }
