param (
    [Parameter(Mandatory = $true)]
    [string]$RegistryName,

    [Parameter(Mandatory = $true)]
    [string]$RepoName
)

$RootDir = Split-Path -Parent $PSScriptRoot
Push-Location $RootDir

$acrLoginServer = "$RegistryName.azurecr.io"
$fullImageName = "$acrLoginServer/$RepoName"

try {
    Write-Host "Logging in to Azure ..." -ForegroundColor Yellow
    az login

    Write-Host "Logging in to ACR..." -ForegroundColor Yellow
    az acr login --name $RegistryName

    Write-Host "Building Docker image '$fullImageName'..." -ForegroundColor Yellow
    docker build --no-cache -t $fullImageName .

    Write-Host "Pushing Docker image to ACR..." -ForegroundColor Yellow
    docker push $fullImageName

    Write-Host "Running Docker container from ACR image (optional)..." -ForegroundColor Yellow
    docker run -p 8080:8080 $fullImageName
}
finally {
    Pop-Location
}
