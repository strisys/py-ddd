param(
    [Parameter(Mandatory=$true)]
    [string]$ClientId,
    
    [Parameter(Mandatory=$true)]
    [string]$Url
)

$scope = "api://$ClientId/.default"

az login

# Fetch token using Azure CLI
$token = az account get-access-token --scope $scope --query accessToken -o tsv
Write-Host $token

$headers = @{
  "Authorization" = "Bearer $token"
  "Accept" = "application/json"
}

Write-Host "Invoking ${Url}"
$response = Invoke-RestMethod -Uri $Url -Method GET -Headers $headers

Write-Host "API Response:"
$response | ConvertTo-Json -Depth 5