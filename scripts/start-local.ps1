param([ValidateSet('backend','frontend')][string]$Service = 'backend')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$servicePort = if ($Service -eq 'backend') { 8000 } else { 5173 }
$checkUrl = if ($Service -eq 'backend') { 'http://127.0.0.1:8000/api/health' } else { 'http://localhost:5173/' }
if (Get-NetTCPConnection -State Listen -LocalPort $servicePort -ErrorAction SilentlyContinue) {
    try {
        $existing = Invoke-WebRequest -Uri $checkUrl -TimeoutSec 5
        $isMizan = if ($Service -eq 'backend') { ($existing.Content | ConvertFrom-Json).version -match '^0\.[12]\.' } else { $existing.Content -match 'MIZAN' }
        if (-not $isMizan) { throw 'Another application is using this port.' }
    } catch { throw "Port $servicePort is already occupied. $($_.Exception.Message)" }
    Write-Host "MIZAN $Service is already running: $checkUrl"
    Write-Host 'Open http://localhost:5173/ in your browser.'
    return
}
Get-Content -LiteralPath (Join-Path $projectRoot '.env') | ForEach-Object {
    if ($_ -match '^([A-Z_]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') }
}
if ($Service -eq 'backend') {
    $env:DATABASE_URL = 'sqlite:///' + (Join-Path $projectRoot 'mizan.db').Replace('\','/')
    $env:EVIDENCE_DIR = Join-Path $projectRoot 'data/evidence'
    Set-Location (Join-Path $projectRoot 'backend')
    & (Join-Path $projectRoot '.venv/Scripts/python.exe') -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) { throw 'Migration failed' }
    & (Join-Path $projectRoot '.venv/Scripts/python.exe') -m app.seed
    if ($LASTEXITCODE -ne 0) { throw 'Seed failed' }
    & (Join-Path $projectRoot '.venv/Scripts/python.exe') -m uvicorn app.main:app --host 127.0.0.1 --port 8000
} else {
    Set-Location (Join-Path $projectRoot 'frontend')
    npm run dev
}
