param (
    [Parameter(Mandatory=$true, HelpMessage="Enter the IP Address of your LinuxONE Server")]
    [string]$IPAddress
)

$keyPath = "$PSScriptRoot\linuxone_key.pem"

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "🚀 INITIATING MAINFRAME UPLINK (s390x)" -ForegroundColor Cyan
Write-Host "Target IP : $IPAddress" -ForegroundColor White
Write-Host "Key Path  : $keyPath" -ForegroundColor White
Write-Host "User      : linux1" -ForegroundColor White
Write-Host "=====================================================" -ForegroundColor Cyan

if (-Not (Test-Path $keyPath)) {
    Write-Host "[ERROR] SSH Key not found!" -ForegroundColor Red
    Write-Host "Please make sure 'linuxone_key.pem' is inside your Project Syn folder." -ForegroundColor Yellow
    exit
}

# Fix permissions for the PEM file (Windows requires restricted permissions for SSH keys)
icacls.exe $keyPath /inheritance:r | Out-Null
icacls.exe $keyPath /grant:r "$($env:USERNAME):R" | Out-Null

Write-Host "✅ Key secured. Establishing connection..." -ForegroundColor Green
Write-Host ""
Write-Host "⚠️ IMPORTANT: When connected, paste the following commands to deploy Project Syn:" -ForegroundColor Yellow
Write-Host "---------------------------------------------------------------------"
Write-Host "git clone https://github.com/yuvrajlokhande19/Project-Syn-IBMZ.git" -ForegroundColor Green
Write-Host "cd Project-Syn-IBMZ" -ForegroundColor Green
Write-Host "bash 03-mainframe-core/deploy_linuxone.sh" -ForegroundColor Green
Write-Host "---------------------------------------------------------------------"
Write-Host ""

ssh -i $keyPath -o StrictHostKeyChecking=no linux1@$IPAddress
