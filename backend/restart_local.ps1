$ErrorActionPreference = "Stop"

$portPids = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique

foreach ($processId in $portPids) {
    Stop-Process -Id $processId -Force
}

Start-Process `
    -FilePath ".venv\Scripts\python.exe" `
    -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload") `
    -WorkingDirectory $PSScriptRoot `
    -WindowStyle Hidden

Start-Sleep -Seconds 6
Invoke-RestMethod http://127.0.0.1:8000/health
