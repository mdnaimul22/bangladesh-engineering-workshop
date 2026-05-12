<#
.SYNOPSIS
    Professional Management Script for BEW ERP (Khulna Server).
    Handles main.py setup, auto-sync (Push Data, Pull Code), and persistence.
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
    $logEntry | Out-File -FilePath $logFile -Append -Encoding UTF8
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
            Stop-Process -Id $p.ProcessId -Force
        }
    }
}

function Start-App {
    Log-Message "Starting application..."
    Start-Process -FilePath $pythonExecutable -ArgumentList $appScript -WorkingDirectory $projectDir -NoNewWindow
}

# --- Action: Status ---
if ($Status) {
    Write-Host "`n--- BEW ERP Status Report (Khulna Server) ---" -ForegroundColor Cyan
    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($task) { Write-Host "[OK] Auto-Startup Task: Registered ($($task.State))" -ForegroundColor Green }
    else { Write-Host "[FAIL] Task NOT Registered" -ForegroundColor Red }
    
    $proc = Get-AppProcess
    if ($proc) { Write-Host "[OK] Application: RUNNING (PID: $($proc.ProcessId | Out-String))" -ForegroundColor Green }
    else { Write-Host "[FAIL] Application: NOT Running" -ForegroundColor Red }
    
    $check = Test-NetConnection -ComputerName "localhost" -Port 5020 -InformationLevel Quiet
    if ($check) { Write-Host "[OK] Port 5020: Listening" -ForegroundColor Green }
    else { Write-Host "[FAIL] Port 5020: Not Listening" -ForegroundColor Red }
    
    if (Test-Path $logFile) {
        $lastLog = Get-Content $logFile -Tail 1 -Encoding UTF8
        Write-Host "[OK] Latest Activity: $lastLog"
    }
    return
}

# --- Action: Stop ---
if ($Stop) {
    Stop-App
    return
}

# --- Action: Setup (Run as Admin) ---
if ($Setup) {
    Write-Host "--- Professional Setup Initialized ---" -ForegroundColor Cyan
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Error "Requires Administrator privileges."
        return
    }
    
    # Register Task pointing to erp.ps1
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File ""$projectDir\erp.ps1"" -Run"
    if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) { Unregister-ScheduledTask -TaskName $taskName -Confirm:$false }
    Register-ScheduledTask -Action $action -Trigger (New-ScheduledTaskTrigger -AtLogOn) -Settings (New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable) -TaskName $taskName -User $env:USERNAME
    
    Write-Host "SETUP COMPLETE! Task Registered to use erp.ps1." -ForegroundColor Green
    Start-ScheduledTask -TaskName $taskName
    return
}

# --- Action: Run (Main Background Sync Loop) ---
if ($Run) {
    Log-Message "Khulna Server Sync Automation Started (using erp.ps1)."
    Set-Location $projectDir
    
    while ($true) {
        try {
            if (-not (Get-AppProcess)) { Start-App }
            
            # Sync Logic
            & $gitExecutable fetch origin main
            $localHash = & $gitExecutable rev-parse HEAD
            $remoteHash = & $gitExecutable rev-parse origin/main
            
            if ($localHash -ne $remoteHash) {
                Log-Message "Remote update (Dhaka) detected. Pulling..."
                # Auto-commit local data changes before pulling to avoid conflicts
                & $gitExecutable add data
                & $gitExecutable commit -m "Auto-save data from Khulna before code update" -ErrorAction SilentlyContinue
                
                & $gitExecutable pull origin main --rebase
                Stop-App
                Start-App
            } else {
                # Check for local data changes to push
                $status = & $gitExecutable status --short data
                if ($status) {
                    Log-Message "Local data changes detected. Pushing to GitHub..."
                    & $gitExecutable add data
                    & $gitExecutable commit -m "Auto-sync data from Khulna"
                    & $gitExecutable push origin main
                }
            }
        } catch {
            Log-Message "Sync Error: $($_.Exception.Message)"
        }
        Start-Sleep -Seconds 600 # Sync every 10 minutes
    }
}
