<#
.SYNOPSIS
    BEW ERP Management Script - Khulna Server
    Strategy:
      - Code updates  : always comes FROM Dhaka (remote wins)
      - Data updates  : always goes TO Dhaka   (local wins)
      - These two are NEVER mixed in the same commit/pull cycle
#>

param(
    [switch]$Setup,
    [switch]$Run,
    [switch]$Status,
    [switch]$Stop
)

$pythonExe  = "C:\Users\PC\AppData\Local\Programs\Python\Python311\python.exe"
$gitExe     = "C:\Program Files\Git\bin\git.exe"
$projectDir = $PSScriptRoot
$appScript  = "main.py"
$logFile    = "$projectDir\automation.log"
$taskName   = "BEW_ERP_Automation"

# ── Helpers ──────────────────────────────────────────────────────────────────

function Write-Log($msg) {
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg"
    Write-Host $line
    try { $line | Out-File $logFile -Append -Encoding UTF8 } catch {}
}

function Get-App {
    Get-CimInstance Win32_Process |
        Where-Object { $_.Name -eq "python.exe" -and $_.CommandLine -like "*$appScript*" }
}

function Stop-App {
    $procs = Get-App
    if ($procs) {
        Write-Log "Stopping app..."
        $procs | ForEach-Object { try { Stop-Process -Id $_.ProcessId -Force } catch {} }
        Start-Sleep -Seconds 2
    }
}

function Start-App {
    Write-Log "Starting app on port 5000..."
    Start-Process -FilePath $pythonExe -ArgumentList $appScript `
                  -WorkingDirectory $projectDir -NoNewWindow
}

function Git($args) {
    & $gitExe -C $projectDir @args 2>&1
}

# ── Status ────────────────────────────────────────────────────────────────────
if ($Status) {
    Write-Host "`n=== BEW ERP Status ===" -ForegroundColor Cyan
    $proc = Get-App
    if ($proc) { Write-Host "[OK]   App: RUNNING (PID $($proc.ProcessId))" -ForegroundColor Green }
    else        { Write-Host "[FAIL] App: NOT RUNNING" -ForegroundColor Red }

    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($task) { Write-Host "[OK]   Task: $($task.State)" -ForegroundColor Green }
    else        { Write-Host "[FAIL] Task: NOT REGISTERED" -ForegroundColor Red }

    $conn = Test-NetConnection -ComputerName localhost -Port 5000 -InformationLevel Quiet
    if ($conn) { Write-Host "[OK]   Port 5000: LISTENING" -ForegroundColor Green }
    else        { Write-Host "[FAIL] Port 5000: NOT LISTENING" -ForegroundColor Red }

    if (Test-Path $logFile) {
        Write-Host "`nLast log entries:" -ForegroundColor Gray
        Get-Content $logFile -Tail 5 -Encoding UTF8
    }
    return
}

# ── Stop ──────────────────────────────────────────────────────────────────────
if ($Stop) { Stop-App; return }

# ── Setup (Admin required) ────────────────────────────────────────────────────
if ($Setup) {
    $me = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
    if (-not $me.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Error "Run as Administrator."; return
    }
    $action = New-ScheduledTaskAction -Execute "powershell.exe" `
              -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File ""$projectDir\erp.ps1"" -Run"
    $trigger  = New-ScheduledTaskTrigger -AtLogOn
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries `
                    -DontStopIfGoingOnBatteries -StartWhenAvailable
    if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }
    Register-ScheduledTask -Action $action -Trigger $trigger -Settings $settings `
                           -TaskName $taskName -User $env:USERNAME
    Write-Host "Task registered. Starting now..." -ForegroundColor Green
    Start-ScheduledTask -TaskName $taskName
    return
}

# ── Run (main loop) ───────────────────────────────────────────────────────────
if ($Run) {
    Write-Log "=== Automation loop started ==="
    Set-Location $projectDir

    while ($true) {
        try {
            # 1. Keep app alive
            if (-not (Get-App)) { Start-App }

            # 2. Check for code updates from Dhaka
            Git fetch, origin, main | Out-Null
            $local  = (Git rev-parse, HEAD) -join ""
            $remote = (Git rev-parse, origin/main) -join ""

            if ($local -ne $remote) {
                Write-Log "Code update found from Dhaka. Syncing..."

                # Backup local data files before touching git
                $dataBackup = "$env:TEMP\bew_data_backup_$(Get-Date -Format 'yyyyMMddHHmmss')"
                Copy-Item "$projectDir\data" $dataBackup -Recurse -Force

                # Reset to remote code (Dhaka wins on code)
                Git reset, --hard, origin/main | Out-Null

                # Restore local data (Khulna wins on data)
                Copy-Item "$dataBackup\*" "$projectDir\data\" -Recurse -Force
                Remove-Item $dataBackup -Recurse -Force

                Write-Log "Code updated. Restarting app..."
                Stop-App
                Start-App

            } else {
                # 3. Push local data changes to GitHub (only data folder)
                $diff = (Git status, --short, data) -join ""
                if ($diff -ne "") {
                    Write-Log "Local data changed. Pushing to GitHub..."
                    Git add, data | Out-Null
                    Git commit, -m, "data: auto-sync from Khulna $(Get-Date -Format 'yyyy-MM-dd HH:mm')" | Out-Null
                    Git push, origin, main | Out-Null
                    Write-Log "Data pushed successfully."
                }
            }
        }
        catch {
            Write-Log "ERROR: $($_.Exception.Message)"
        }

        Start-Sleep -Seconds 600  # check every 10 minutes
    }
}
