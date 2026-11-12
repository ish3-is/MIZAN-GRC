$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$envPath = Join-Path $projectRoot '.env'
if (Test-Path -LiteralPath $envPath) { throw '.env already exists. Preserve existing evidence keys.' }
function New-RandomHex([int]$count) {
    $bytes = New-Object byte[] $count
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
    return ([BitConverter]::ToString($bytes)).Replace('-', '').ToLower()
}
$keyBytes = New-Object byte[] 32
$keyRng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
try { $keyRng.GetBytes($keyBytes) } finally { $keyRng.Dispose() }
$evidenceKey = [Convert]::ToBase64String($keyBytes).Replace('+','-').Replace('/','_')
$contents = "POSTGRES_PASSWORD=$(New-RandomHex 24)`nDEMO_PASSWORD=$(New-RandomHex 16)`nEVIDENCE_KEY=$evidenceKey`n"
[IO.File]::WriteAllText($envPath, $contents, (New-Object Text.UTF8Encoding($false)))
Write-Host 'Created local .env. Read DEMO_PASSWORD there; do not share or commit it.'
