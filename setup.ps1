# Run this script to create the full project structure
# Usage: .\setup.ps1

mkdir bot, bot\adapters, bot\adapters\telegram, bot\adapters\telegram\handlers, bot\adapters\telegram\views, bot\app, bot\core, bot\core\services, bot\infra, bot\infra\db, bot\infra\cache, bot\infra\scheduler, bot\infra\http, bot\tests

New-Item -Path "bot\adapters\telegram\handlers\__init__.py" -ItemType File
New-Item -Path "bot\adapters\telegram\views\__init__.py" -ItemType File
New-Item -Path "bot\adapters\telegram\__init__.py" -ItemType File
New-Item -Path "bot\adapters\__init__.py" -ItemType File
New-Item -Path "bot\app\__init__.py" -ItemType File
New-Item -Path "bot\core\services\__init__.py" -ItemType File
New-Item -Path "bot\core\__init__.py" -ItemType File
New-Item -Path "bot\infra\db\__init__.py" -ItemType File
New-Item -Path "bot\infra\cache\__init__.py" -ItemType File
New-Item -Path "bot\infra\scheduler\__init__.py" -ItemType File
New-Item -Path "bot\infra\http\__init__.py" -ItemType File
New-Item -Path "bot\infra\__init__.py" -ItemType File
New-Item -Path "bot\tests\__init__.py" -ItemType File
New-Item -Path "bot\__init__.py" -ItemType File

Write-Host "Project structure created successfully"
