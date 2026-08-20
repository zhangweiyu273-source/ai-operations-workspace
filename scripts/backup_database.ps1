param([string]$OutputDirectory = "backups")
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$docker = Join-Path $env:LOCALAPPDATA "Programs\DockerDesktop\resources\bin\docker.exe"
if (-not (Test-Path $docker)) { $docker = "docker" }
Push-Location $root
try {
  New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  $file = Join-Path $OutputDirectory "ai_ops-$stamp.dump"
  $settings = @{}
  Get-Content .env | Where-Object { $_ -match '^[A-Z0-9_]+=' } | ForEach-Object { $key, $value = $_ -split '=', 2; $settings[$key] = $value }
  $db = $settings['POSTGRES_DB']; if (-not $db) { $db="ai_ops" }
  $user = $settings['POSTGRES_USER']; if (-not $user) { $user="ai_ops" }
  $containerId = (& $docker compose ps -q db).Trim()
  if (-not $containerId) { throw "Database container is not running" }
  $containerFile = "/tmp/ai_ops-$stamp.dump"
  & $docker compose exec -T db pg_dump -U $user -Fc -f $containerFile $db
  if ($LASTEXITCODE -ne 0) { throw "Backup failed" }
  & $docker cp "${containerId}:$containerFile" $file
  & $docker compose exec -T db rm -f $containerFile | Out-Null
  if ($LASTEXITCODE -ne 0 -or -not (Test-Path $file) -or (Get-Item $file).Length -eq 0) { throw "Backup failed" }
  Write-Output "Backup created: $file"
} finally { Pop-Location }
