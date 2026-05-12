<#
.SYNOPSIS
    Professional Management Script for BEW ERP (Khulna Server).
    Updated to handle main.py and auto-sync.
#>

param(
    [switch]$Setup,
    [switch]$Run,
    [switch]$Status,
    [switch]$Stop
)

$pythonExecutable = "C:\Users\PC\AppData\Local\Programs\Python\Python311\python.exe"
$gitExecutable = "C:\Program Files\Git\bin\git.exe"
$projectDir = $PSScriptRoot
$appScript = "main.py"
$logFile = "$projectDir\automation.log"
$taskName = "BEW_ERP_Automation"

function Log-Message($message) {
    if (-not (Test-Path $projectDir)) { return }
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $message"
    Write-Host $logEntry
    try { $logEntry | Out-File -FilePath $logFile -Append -Encoding UTF8 } catch {}
}

function Get-AppProcess {
    return Get-CimInstance Win32_Process | Where-Object { 
        $_.Name -eq "python.exe" -and ($_.CommandLine -like "*$appScript*" -or $_.CommandLine -like "*flask*")
    }
}

function Stop-App {
    $processes = Get-AppProcess
    if ($processes) {
        Log-Message "Stopping application processes..."
        foreach ($p in $processes) {
            try { Stop-Process -Id $p.ProcessId -Force } catch {}
        }
    }
}

function Start-App {
    Log-Message "Starting application..."
    Start-Process -FilePath $pythonExecutable -ArgumentList $appScript -WorkingDirectory $projectDir -NoNewWindow
}

if ($Status) {
    Write-Host "`n--- BEW ERP Status Report ---" -ForegroundColor Cyan
    $proc = Get-AppProcess
    if ($proc) { Write-Host "[OK] Application: RUNNING" -ForegroundColor Green }
    else { Write-Host "[FAIL] Application: NOT Running" -ForegroundColor Red }
    return
}

if ($Stop) {
    Stop-App
    return
}

if ($Run) {
    Log-Message "Automation Started."
    Set-Location $projectDir
    
    while ($true) {
        try {
            if (-not (Get-AppProcess)) { Start-App }
            
            # Simple sync: only push if data changes, only pull if code updates
            Invoke-Expression "& '$gitExecutable' fetch origin main"
            $local = Invoke-Expression "& '$gitExecutable' rev-parse HEAD"
            $remote = Invoke-Expression "& '$gitExecutable' rev-parse origin/main"
            
            if ("$local" -ne "$remote") {
                Log-Message "Update detected. Pulling..."
                Invoke-Expression "& '$gitExecutable' add data"
                Invoke-Expression "& '$gitExecutable' commit -m 'Auto-save data before update'"
                Invoke-Expression "& '$gitExecutable' pull origin main --rebase"
                Stop-App
                Start-App
            } else {
                $diff = Invoke-Expression "& '$gitExecutable' status --short data"
                if ("$diff" -ne "") {
                    Log-Message "Data changed. Pushing..."
                    Invoke-Expression "& '$gitExecutable' add data"
                    Invoke-Expression "& '$gitExecutable' commit -m 'Auto-sync from Khulna'"
                    Invoke-Expression "& '$gitExecutable' push origin main"
                }
            }
        } catch {
            Log-Message "Sync Error: $($_.Exception.Message)"
        }
        Start-Sleep -Seconds 600
    }
}
