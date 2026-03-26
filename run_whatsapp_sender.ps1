Add-Type -AssemblyName System.Windows.Forms

$secondary = [System.Windows.Forms.Screen]::AllScreens | Where-Object { -not $_.Primary } | Select-Object -First 1

if (-not $secondary) {
    Write-Host "No secondary monitor found."
    exit
}

$p = Start-Process cmd -ArgumentList '/k cd /d C:\Users\Falec\OneDrive\Documentos\Python\WhatsApp_Good_Morning && venv\Scripts\python.exe main.py && echo. && echo ============================== && echo    Press any key to close && echo ============================== && pause >nul && exit' -PassThru

Start-Sleep -Milliseconds 1000

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
}
"@

$x = $secondary.Bounds.X
$y = $secondary.Bounds.Y
$w = [Math]::Min(1080, $secondary.Bounds.Width)
$h = [Math]::Min(820, $secondary.Bounds.Height)

[Win32]::MoveWindow($p.MainWindowHandle, $x, $y, $w, $h, $true)