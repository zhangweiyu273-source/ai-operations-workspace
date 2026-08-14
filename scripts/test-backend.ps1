$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$docker = Join-Path $env:LOCALAPPDATA "Programs\DockerDesktop\resources\bin\docker.exe"
if (-not (Test-Path $docker)) { $docker = "docker" }

Push-Location $projectRoot
try {
    & $docker compose --profile test up -d test-db
    if ($LASTEXITCODE -ne 0) { throw "test-db failed to start" }
    & $docker compose --profile test build test-migrate
    if ($LASTEXITCODE -ne 0) { throw "test migration image build failed" }
    & $docker compose --profile test run --rm test-migrate
    if ($LASTEXITCODE -ne 0) { throw "test migration failed" }

    $settings = @{}
    Get-Content .env | Where-Object { $_ -match '^[A-Z0-9_]+=' } | ForEach-Object {
        $key, $value = $_ -split '=', 2
        $settings[$key] = $value
    }
    $env:TEST_DATABASE_URL = $settings["TEST_DATABASE_URL"]
    if (-not $env:TEST_DATABASE_URL -or $env:TEST_DATABASE_URL -notmatch '/[^/]*_test$') {
        throw "TEST_DATABASE_URL must target a *_test database"
    }
    & "backend\.venv\Scripts\python.exe" -m pytest backend
    if ($LASTEXITCODE -ne 0) { throw "backend tests failed" }
}
finally {
    Pop-Location
}
