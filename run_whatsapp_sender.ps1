Add-Type -AssemblyName System.Windows.Forms

# ==============================
# PATH RESOLUTION
# ==============================
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogsDir = Join-Path $ProjectRoot "logs"
$LauncherLog = Join-Path $LogsDir "launcher.log"
$VenvPython = Join-Path $ProjectRoot "venv\Scripts\python.exe"
$MainPy = Join-Path $ProjectRoot "main.py"

# Ensure logs directory exists
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir | Out-Null
}

function Write-LauncherLog {
    param(
        [string]$Level,
        [string]$Message
    )

    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $Line = "[$Timestamp] [$Level] $Message"

    Write-Host $Line
    Add-Content -Path $LauncherLog -Value $Line
}

Write-LauncherLog -Level "INFO" -Message "Launcher started."
Write-LauncherLog -Level "INFO" -Message "Project root: $ProjectRoot"

# ==============================
# FILE VALIDATION
# ==============================
if (-not (Test-Path $MainPy)) {
    Write-LauncherLog -Level "ERROR" -Message "main.py not found: $MainPy"
    pause
    exit 1
}

# ==============================
# PYTHON RESOLUTION
# ==============================
$PythonExe = $null

if (Test-Path $VenvPython) {
    $PythonExe = $VenvPython
    Write-LauncherLog -Level "INFO" -Message "Using Python from virtual environment: $PythonExe"
}
else {
    Write-LauncherLog -Level "WARNING" -Message "Virtual environment Python not found. Trying system Python."

    try {
        $SystemPythonCommand = Get-Command python -ErrorAction Stop
        $PythonExe = $SystemPythonCommand.Source
        Write-LauncherLog -Level "INFO" -Message "Using system Python: $PythonExe"
    }
    catch {
        Write-LauncherLog -Level "ERROR" -Message "No Python executable found. Create the venv or install Python."
        pause
        exit 1
    }
}

# ==============================
# TERMINAL COMMAND
# ==============================
$CmdCommand = "/k cd /d `"$ProjectRoot`" && `"$PythonExe`" `"$MainPy`" && echo. && echo ============================== && echo    Press any key to close && echo ============================== && pause >nul && exit"

Write-LauncherLog -Level "INFO" -Message "Starting terminal process."

$Process = Start-Process cmd.exe -ArgumentList $CmdCommand -PassThru

# Wait so the terminal window handle becomes available
Start-Sleep -Milliseconds 1200

# ==============================
# WINDOW POSITIONING
# ==============================
Add-Type @"
using System;
using System.Runtime.InteropServices;

public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
}
"@

$AllScreens = [System.Windows.Forms.Screen]::AllScreens
$PrimaryScreen = $AllScreens | Where-Object { $_.Primary } | Select-Object -First 1
$SecondaryScreen = $AllScreens | Where-Object { -not $_.Primary } | Select-Object -First 1

if ($SecondaryScreen) {
    $TargetScreen = $SecondaryScreen
    Write-LauncherLog -Level "INFO" -Message "Secondary monitor detected. Using secondary screen."
}
else {
    $TargetScreen = $PrimaryScreen
    Write-LauncherLog -Level "WARNING" -Message "No secondary monitor detected. Falling back to primary screen."
}

$X = $TargetScreen.Bounds.X
$Y = $TargetScreen.Bounds.Y
$Width = [Math]::Min(1800, $TargetScreen.Bounds.Width)
$Height = [Math]::Min(900, $TargetScreen.Bounds.Height)

if ($Process.MainWindowHandle -ne 0) {
    [Win32]::MoveWindow($Process.MainWindowHandle, $X, $Y, $Width, $Height, $true) | Out-Null
    Write-LauncherLog -Level "INFO" -Message "Terminal window positioned successfully."
}
else {
    Write-LauncherLog -Level "WARNING" -Message "Could not access terminal window handle to reposition it."
}

Write-LauncherLog -Level "INFO" -Message "Launcher finished."