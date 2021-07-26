param($Directory)

Set-ItemProperty -Path $Directory -Name LastWriteTime  -Value $(Get-Date)
