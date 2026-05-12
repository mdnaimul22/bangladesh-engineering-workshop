<#
.SYNOPSIS
    Professional Management Script for BEW ERP.
    Handles setup, auto-sync, and persistence.

.EXAMPLE
    .\manage_erp.ps1 -Setup (Run as Admin)
    .\manage_erp.ps1 -Status
    .\manage_erp.ps1 -Run
#>

param(
    [switch]$Setup,
    [switch]$Run,
    [switch]$Status,
    [switch]$Stop
)

$pythonExecutable = "C:\Users\PC\AppData\Local\Programs\Python\Python311\python.exe"
$gitExecutable = "C:\Program Files\Git\bin\git.exe"
$projectDir = "E:\bangladesh-engineering-workshop"
$appScript = "app.py"
$logFile = "$projectDir\automation.log"
$taskName = "BEW_ERP_Automation"

function Log-Message($message) {
    if (-not (Test-Path $projectDir)) { return }
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $message"
    Write-Host $logEntry
    $logEntry | Out-File -FilePath $logFile -Append
}

function Get-AppProcess {
    # Using Get-CimInstance for better performance and robustness in PowerShell 5.1+
    return Get-CimInstance Win32_Process | Where-Object { 
        $_.Name -eq "python.exe" -and ($_.CommandLine -like "*$appScript*" -or $_.CommandLine -like "*flask*")
    }
}

function Stop-App {
    $processes = Get-AppProcess
    if ($processes) {
        Write-Host "Stopping application processes..."
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
    Write-Host "`n--- BEW ERP Status Report ---" -ForegroundColor Cyan
    
    # 1. Check Service Task
    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($task) {
        Write-Host "[OK] Auto-Startup Task: Registered (State: $($task.State))" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Auto-Startup Task: NOT Registered (Run -Setup as Admin)" -ForegroundColor Red
    }
    
    # 2. Check Process
    $proc = Get-AppProcess
    if ($proc) {
        $pids = $proc.ProcessId -join ", "
        Write-Host "[OK] Application Process: RUNNING (PIDs: $pids)" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Application Process: NOT Running" -ForegroundColor Red
    }

    # 3. Check Network Reachability
    try {
        $check = Test-NetConnection -ComputerName "localhost" -Port 5020 -InformationLevel Quiet
        if ($check) {
            Write-Host "[OK] Network Port 5020: LISTENING (App is reachable)" -ForegroundColor Green
        } else {
            Write-Host "[FAIL] Network Port 5020: NOT Listening" -ForegroundColor Red
        }
    } catch {
        Write-Host "[FAIL] Network Check: Error occurred" -ForegroundColor Yellow
    }
    
    # 4. Check Log
    if (Test-Path $logFile) {
        $lastLog = Get-Content $logFile -Tail 1 -Encoding Unicode
        Write-Host "[OK] Latest Sync Activity: $lastLog"
    }
    Write-Host "`nAccess URL: http://localhost:5020" -ForegroundColor Gray
    return
}

# --- Action: Stop ---
if ($Stop) {
    Stop-App
    Write-Host "Application stopped."
    return
}

# --- Action: Setup ---
if ($Setup) {
    Write-Host "--- Professional Setup Initialized ---" -ForegroundColor Cyan
    
    # 1. Admin Check
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Error "CRITICAL: This setup requires Administrator privileges."
        Write-Host "`nPlease run PowerShell as Administrator and try again." -ForegroundColor Yellow
        return
    }
    
    # 2. Fix PATH persistently
    Write-Host "Fixing PATH for user..."
    $pythonScripts = "$($pythonExecutable | Split-Path)\Scripts"
    $gitCmd = "$($gitExecutable | Split-Path)\cmd"
    $newPaths = @($($pythonExecutable | Split-Path), $pythonScripts, $gitCmd, $($gitExecutable | Split-Path))
    $currentPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $updatedPath = ($newPaths + ($currentPath -split ";" | Where-Object { $newPaths -notcontains $_ })) -join ";"
    [System.Environment]::SetEnvironmentVariable("Path", $updatedPath, "User")
    $env:Path = $updatedPath
    
    # 3. Register Scheduled Task
    Write-Host "Configuring auto-startup task..."
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File ""$projectDir\manage_erp.ps1"" -Run"
    if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) { Unregister-ScheduledTask -TaskName $taskName -Confirm:$false }
    Register-ScheduledTask -Action $action -Trigger (New-ScheduledTaskTrigger -AtLogOn) -Settings (New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable) -TaskName $taskName -User $env:USERNAME
    
    # 4. Finalize
    Write-Host "`nSETUP COMPLETE! The system is now ready." -ForegroundColor Green
    Write-Host "Starting the application loop now..."
    Start-ScheduledTask -TaskName $taskName
    return
}

# --- Action: Run (Main Background Loop) ---
if ($Run) {
    Log-Message "Background automation started."
    Set-Location $projectDir
    
    while ($true) {
        try {
            # Start app if not running
            if (-not (Get-AppProcess)) { Start-App }
            
            # Check for Git Updates
            & $gitExecutable fetch origin main
            if ((& $gitExecutable rev-parse HEAD) -ne (& $gitExecutable rev-parse origin/main)) {
                Log-Message "New update detected! Pulling and restarting..."
                Stop-App
                & $gitExecutable pull origin main
                & $pythonExecutable -m pip install -r requirements.txt
                Start-App
            }
        } catch {
            Log-Message "Error: $($_.Exception.Message)"
        }
        Start-Sleep -Seconds 300
    }
}

# If no switch provided, show help
Write-Host "Usage: .\manage_erp.ps1 [-Setup] [-Status] [-Run] [-Stop]"
Write-Host "-Setup: Register Task, Fix Path (Needs Admin)"
Write-Host "-Status: Check current state"
Write-Host "-Run: Start background monitoring loop"
Write-Host "-Stop: Stop the application"
