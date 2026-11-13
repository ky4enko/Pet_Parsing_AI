#requires -Version 5.1
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$EntryPoint = Join-Path $ProjectRoot "app\ui\main_window.py"
$SourceEnv = Join-Path $ProjectRoot ".env"
$AssetsSource = Join-Path $ProjectRoot "app\ui\assets"
$IconSource = Join-Path $PSScriptRoot "AUTO_RIA_Analyzer.ico"
$RuntimeHook = Join-Path $PSScriptRoot "load_env_runtime_hook.py"

$DistRoot = Join-Path $ProjectRoot "dist"
$AppDist = Join-Path $DistRoot "Pet_Parsing_AI"
$ExePath = Join-Path $AppDist "Pet_Parsing_AI.exe"
$WorkRoot = Join-Path $ProjectRoot "build\pyinstaller"

function Stop-Build([string]$Message) {
    Write-Host ""
    Write-Host "ОШИБКА: $Message" -ForegroundColor Red
    Write-Host ""
    Read-Host "Нажми Enter для выхода"
    exit 1
}

function Copy-DirectoryContents([string]$Source, [string]$Destination) {
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    $Children = @(Get-ChildItem -LiteralPath $Source -Force)
    foreach ($Child in $Children) {
        Copy-Item -LiteralPath $Child.FullName -Destination $Destination -Recurse -Force
    }
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor DarkGray
Write-Host "          AUTO.RIA ANALYZER — BUILDER" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor DarkGray
Write-Host ""

# Validate the actual project files before doing anything.
if (-not (Test-Path -LiteralPath $Python)) {
    Stop-Build "Не найден Python виртуального окружения: $Python"
}
if (-not (Test-Path -LiteralPath $EntryPoint)) {
    Stop-Build "Не найден app\ui\main_window.py."
}
if (-not (Test-Path -LiteralPath $SourceEnv)) {
    Stop-Build "Не найден .env в корне проекта. Сборка остановлена."
}
if (-not (Test-Path -LiteralPath $AssetsSource)) {
    Stop-Build "Не найдена папка app\ui\assets."
}
if (-not (Test-Path -LiteralPath $IconSource)) {
    Stop-Build "Не найдена иконка AUTO_RIA_Analyzer.ico рядом со сборщиком."
}

# Validate all six resources used by the current UI/theme manager.
$RequiredAssets = @(
    "muscle_car.png",
    "background1.jpg",
    "background2.jpg",
    "background3.jpg",
    "background4.jpg",
    "background5.jpg"
)
foreach ($AssetName in $RequiredAssets) {
    if (-not (Test-Path -LiteralPath (Join-Path $AssetsSource $AssetName))) {
        Stop-Build "В app\ui\assets не найден файл $AssetName."
    }
}
$AssetFiles = @(Get-ChildItem -LiteralPath $AssetsSource -File -Recurse -ErrorAction SilentlyContinue)
Write-Host "Исходные ресурсы проверены: $($AssetFiles.Count) файлов." -ForegroundColor Green
Write-Host "Файл .env найден. Его содержимое будет скопировано ПОЛНОСТЬЮ и БЕЗ ИЗМЕНЕНИЙ." -ForegroundColor Green

# If a previous EXE exists, repair its packaging instead of making the user wait
# for another PyInstaller run. A fresh compile happens only when the EXE is absent.
$ExistingExe = Test-Path -LiteralPath $ExePath

if (-not $ExistingExe) {
    Write-Host ""
    Write-Host "Готового EXE нет — запускаю полную компиляцию." -ForegroundColor Cyan

    if (-not (Test-Path -LiteralPath $RuntimeHook)) {
        Stop-Build "Не найден load_env_runtime_hook.py."
    }

    Write-Host "[1/4] Проверяю зависимости..." -ForegroundColor Yellow
    & $Python -c "import PySide6, shiboken6, qfluentwidgets, dotenv, requests"
    if ($LASTEXITCODE -ne 0) {
        Stop-Build "В .venv отсутствует одна из зависимостей приложения (PySide6, qfluentwidgets, python-dotenv или requests)."
    }

    & $Python -m pip show pyinstaller *> $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Устанавливаю PyInstaller в .venv..." -ForegroundColor Yellow
        & $Python -m pip install pyinstaller
        if ($LASTEXITCODE -ne 0) {
            Stop-Build "Не удалось установить PyInstaller."
        }
    }

    New-Item -ItemType Directory -Force -Path $DistRoot | Out-Null
    New-Item -ItemType Directory -Force -Path $WorkRoot | Out-Null

    # Preserve any old output before rebuilding.
    if (Test-Path -LiteralPath $AppDist) {
        $Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $BackupPath = Join-Path $DistRoot "Pet_Parsing_AI_previous_$Stamp"
        Move-Item -LiteralPath $AppDist -Destination $BackupPath
        Write-Host "Старая сборка сохранена: $BackupPath" -ForegroundColor Yellow
    }

    Write-Host "[2/4] Компилирую приложение..." -ForegroundColor Yellow
    $PyInstallerArgs = @(
        "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--windowed",
        "--name", "Pet_Parsing_AI",
        "--icon", $IconSource,
        "--paths", $ProjectRoot,
        "--add-data", "$AssetsSource;app/ui/assets",
        "--runtime-hook", $RuntimeHook,
        "--collect-all", "PySide6",
        "--collect-all", "shiboken6",
        "--collect-all", "qfluentwidgets",
        "--collect-all", "dotenv",
        "--collect-all", "requests",
        "--collect-submodules", "app",
        "--hidden-import", "backend_client",
        "--distpath", $DistRoot,
        "--workpath", $WorkRoot,
        "--specpath", $WorkRoot,
        $EntryPoint
    )

    Push-Location $ProjectRoot
    try {
        & $Python @PyInstallerArgs
        if ($LASTEXITCODE -ne 0) {
            Stop-Build "PyInstaller завершился с ошибкой. Предыдущая сборка сохранена в dist."
        }
    }
    finally {
        Pop-Location
    }

    if (-not (Test-Path -LiteralPath $ExePath)) {
        Stop-Build "PyInstaller завершился, но Pet_Parsing_AI.exe не найден."
    }
}
else {
    Write-Host "Найден готовый EXE. Повторную компиляцию пропускаю — исправляю его комплектность." -ForegroundColor Green
}

# PyInstaller 6 uses _internal; older versions place files directly in the app folder.
$InternalDir = Join-Path $AppDist "_internal"
if (Test-Path -LiteralPath $InternalDir) {
    $BundleRoot = $InternalDir
}
else {
    $BundleRoot = $AppDist
}

Write-Host ""
Write-Host "Копирую полный .env без чтения, фильтрации или изменения..." -ForegroundColor Yellow

# Keep a copy beside the EXE and, critically, beside bundled Python modules.
# backend_client.py and backend/config.py load .env relative to their __file__.
$EnvTargets = @(
    (Join-Path $AppDist ".env"),
    (Join-Path $BundleRoot ".env")
) | Select-Object -Unique

foreach ($EnvTarget in $EnvTargets) {
    Copy-Item -LiteralPath $SourceEnv -Destination $EnvTarget -Force
}

$SourceHash = (Get-FileHash -LiteralPath $SourceEnv -Algorithm SHA256).Hash
foreach ($EnvTarget in $EnvTargets) {
    $TargetHash = (Get-FileHash -LiteralPath $EnvTarget -Algorithm SHA256).Hash
    if ($TargetHash -ne $SourceHash) {
        Stop-Build "Проверка .env не пройдена: копия отличается от исходного файла."
    }
}
Write-Host ".env скопирован целиком. SHA256 совпадает с исходным файлом." -ForegroundColor Green

Write-Host "Копирую изображения и фоны..." -ForegroundColor Yellow

# Copy assets to the normal PyInstaller bundle location and also beside the EXE.
# This supports both PyInstaller 6 (_internal) and older onedir layouts.
$AssetTargets = @(
    (Join-Path $BundleRoot "app\ui\assets"),
    (Join-Path $AppDist "app\ui\assets")
) | Select-Object -Unique

foreach ($AssetTarget in $AssetTargets) {
    Copy-DirectoryContents -Source $AssetsSource -Destination $AssetTarget

    foreach ($AssetName in $RequiredAssets) {
        if (-not (Test-Path -LiteralPath (Join-Path $AssetTarget $AssetName))) {
            Stop-Build "Не удалось перенести $AssetName в $AssetTarget."
        }
    }
}
Write-Host "Все изображения и пять фонов перенесены и проверены." -ForegroundColor Green

# Install the final icon next to the executable and create the desktop shortcut.
$IconInDist = Join-Path $AppDist "AUTO_RIA_Analyzer.ico"
Copy-Item -LiteralPath $IconSource -Destination $IconInDist -Force

$Desktop = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $Desktop "AUTO.RIA Analyzer.lnk"
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $ExePath
$Shortcut.WorkingDirectory = $AppDist
$Shortcut.IconLocation = "$IconInDist,0"
$Shortcut.Description = "AUTO.RIA Analyzer — AI Market Analysis"
$Shortcut.WindowStyle = 1
$Shortcut.Save()

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "ГОТОВО. ПРИЛОЖЕНИЕ ПОДГОТОВЛЕНО." -ForegroundColor Green
Write-Host "EXE: $ExePath" -ForegroundColor White
Write-Host "Ярлык: $ShortcutPath" -ForegroundColor White
Write-Host ".env: полный, без изменений (проверен SHA256)." -ForegroundColor White
Write-Host "Ресурсы: $($AssetFiles.Count) файлов, включая все 5 фонов." -ForegroundColor White
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Запускаю AUTO.RIA Analyzer..." -ForegroundColor Cyan

try {
    Start-Process -FilePath $ExePath -WorkingDirectory $AppDist
    Write-Host "Приложение запущено. В дальнейшем запускай его ярлыком с рабочего стола." -ForegroundColor Green
}
catch {
    Write-Host "Не удалось автоматически открыть приложение: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Попробуй запустить ярлык AUTO.RIA Analyzer на рабочем столе."
}

Write-Host ""
Read-Host "Нажми Enter для закрытия"
