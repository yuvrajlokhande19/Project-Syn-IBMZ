param (
    [Parameter(Mandatory=$true)]
    [string]$IPAddress,
    
    [Parameter(Mandatory=$true)]
    [string]$Username
)

$sshDir = "$env:USERPROFILE\.ssh"
$configFile = "$sshDir\config"

if (-not (Test-Path -Path $sshDir)) {
    New-Item -ItemType Directory -Path $sshDir | Out-Null
    Write-Host "Created .ssh directory."
}

$configEntry = @"

# ==========================================
# PROJECT SYN: IBM LinuxONE Staging Server
# ==========================================
Host linuxone
    HostName $IPAddress
    User $Username
    Port 22
    StrictHostKeyChecking no
    ServerAliveInterval 60
"@

Add-Content -Path $configFile -Value $configEntry
Write-Host "✅ SUCCESS! IBM LinuxONE instance added to your laptop's SSH config."
Write-Host "You can now connect instantly by opening any terminal and typing:"
Write-Host "ssh linuxone"
Write-Host ""
Write-Host "Next Step: Run the deployment script once connected:"
Write-Host "git clone https://github.com/yuvrajlokhande19/Project-Syn-IBMZ.git"
Write-Host "bash Project-Syn-IBMZ/03-mainframe-core/deploy_linuxone.sh"
