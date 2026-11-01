$ErrorActionPreference = 'Stop'
$env:ASPNETCORE_ENVIRONMENT = 'Development'
$project = Join-Path $PSScriptRoot 'be.qlythuvien\qlthuvien_vip.csproj'
dotnet run --project $project --no-launch-profile --urls http://localhost:5160
