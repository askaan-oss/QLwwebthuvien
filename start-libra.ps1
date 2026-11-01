$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$logDir = Join-Path $PSScriptRoot 'logs'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
function Test-LibraUrl([string]$url) {
    try { $r=Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 3; return $r.StatusCode -eq 200 } catch { return $false }
}
try {
    $api='http://localhost:5160/api/Products?pageSize=1'
    if (-not (Test-LibraUrl $api)) {
        $listener=Get-NetTCPConnection -LocalPort 5160 -State Listen -ErrorAction SilentlyContinue
        if ($listener) { throw 'Cong 5160 dang duoc su dung nhung API khong phan hoi. Kiem tra backend/SQL Server, khong khoi dong trung.' }
        $backendScript=Join-Path $PSScriptRoot 'start-backend.ps1'
        Start-Process powershell.exe -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',('"'+$backendScript+'"')) -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDir 'backend.log') -RedirectStandardError (Join-Path $logDir 'backend-error.log') | Out-Null
    }
    $ready=$false
    for($i=0;$i -lt 40;$i++) {
        if(Test-LibraUrl $api){$ready=$true;break}
        Start-Sleep -Seconds 1
    }
    if(-not $ready){throw 'Backend chua san sang. Xem logs/backend-error.log va logs/backend.log.'}
    if(-not (Test-LibraUrl 'http://127.0.0.1:4173/')) {
        $nodeCommand=Get-Command node.exe -ErrorAction SilentlyContinue
        $nodePath=if($nodeCommand){$nodeCommand.Source}else{Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'}
        if(-not (Test-Path -LiteralPath $nodePath)){throw 'Chua tim thay Node.js. Hay cai Node.js de chay giao dien.'}
        $server=Join-Path $PSScriptRoot 'server.cjs'
        Start-Process -FilePath $nodePath -ArgumentList ('"'+$server+'"') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDir 'frontend.log') -RedirectStandardError (Join-Path $logDir 'frontend-error.log') | Out-Null
    }
    $ready=$false
    for($i=0;$i -lt 10;$i++) {if(Test-LibraUrl 'http://127.0.0.1:4173/'){$ready=$true;break};Start-Sleep -Seconds 1}
    if(-not $ready){throw 'Giao dien chua san sang. Xem logs/frontend-error.log.'}
    Write-Host 'Libra da san sang: http://127.0.0.1:4173/' -ForegroundColor Green
    Start-Process 'http://127.0.0.1:4173/'
} catch { Write-Host $_.Exception.Message -ForegroundColor Red; exit 1 }
