<#
Create a Desktop shortcut that launches the `start_backend.bat` script.

Usage (PowerShell):
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    .\create_shortcut.ps1
#>
$WScriptShell = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')
$shortcutPath = Join-Path $desktop 'Start PII Backend.lnk'
$target = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Definition) 'start_backend.bat'
$shortcut = $WScriptShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $target
$shortcut.WorkingDirectory = Split-Path -Parent $target
$shortcut.WindowStyle = 1
$shortcut.IconLocation = "$target,0"
$shortcut.Save()
Write-Output "Created shortcut: $shortcutPath"
