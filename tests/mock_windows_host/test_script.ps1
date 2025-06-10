# Sample PowerShell test script
Write-Output "Running PowerShell script from mock Windows host"
Write-Output "Environment Information:"
Write-Output "OS: $env:OS"
Write-Output "Computer Name: $env:COMPUTERNAME"
Write-Output "User: $env:USERNAME"
Write-Output "Current Path: $(Get-Location)"

# Create some test files to demonstrate file operations
$TestPath = "C:\TestFolder"
if (-not (Test-Path $TestPath)) {
    New-Item -Path $TestPath -ItemType Directory
}

"Hello from PowerShell" | Out-File -FilePath "$TestPath\test.txt"
"This is another test file" | Out-File -FilePath "$TestPath\another.txt"

Get-ChildItem -Path $TestPath
