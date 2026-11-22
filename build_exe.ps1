# Builds the Windows application:  dist\EcoQuest\EcoQuest.exe
# Needs:  pip install pyinstaller pywebview waitress
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

python -m PyInstaller --noconfirm --clean --windowed --name EcoQuest `
    --icon "static\images\ecoquest.ico" `
    --add-data "templates;templates" --add-data "static;static" --add-data "database;database" `
    --hidden-import pymysql --hidden-import cryptography --hidden-import waitress `
    --collect-all webview `
    desktop_app.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

# settings (database login) live next to the program
Copy-Item (Join-Path $root ".env") (Join-Path $root "dist\EcoQuest\.env") -Force
New-Item -ItemType Directory -Force (Join-Path $root "dist\EcoQuest\logs") | Out-Null
Write-Output "Built: $root\dist\EcoQuest\EcoQuest.exe"
