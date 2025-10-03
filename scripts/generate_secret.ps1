<#
Generates a secure SECRET_KEY and optionally writes it to .env in the project root.
Usage:
  # just print
  .\generate_secret.ps1
  # generate and write to .env (will overwrite existing SECRET_KEY line)
  .\generate_secret.ps1 -WriteToEnv
#>
param(
  [switch]$WriteToEnv
)

# generate 32 bytes and base64 encode
$bytes = New-Object 'System.Byte[]' 32
[System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
$secret = [System.Convert]::ToBase64String($bytes)

Write-Host "Generated SECRET_KEY: $secret"

if($WriteToEnv){
  $envFile = Join-Path -Path (Get-Location) -ChildPath ".env"
  if(Test-Path $envFile){
    (Get-Content $envFile) | ForEach-Object {
      if($_ -match '^SECRET_KEY='){
        "SECRET_KEY=$secret"
      } else { $_ }
    } | Set-Content $envFile
    Write-Host "Updated existing .env with new SECRET_KEY."
  } else {
    "SECRET_KEY=$secret" | Out-File -FilePath $envFile -Encoding utf8
    Write-Host "Created .env with SECRET_KEY."
  }
}
