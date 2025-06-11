$RootDir = Split-Path -Parent $PSScriptRoot
Push-Location $RootDir

try {
    Write-Host "Building Docker image..." -ForegroundColor Yellow
    docker build --build-arg BUILD_CONTEXT=local -t py-ddd-api .
    
    Write-Host "Running Docker container..." -ForegroundColor Yellow
    docker run -p 8080:8080 py-ddd-api
}
finally {
    Pop-Location
}