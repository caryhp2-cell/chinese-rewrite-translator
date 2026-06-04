param(
    [string]$Python = ".\.venv\Scripts\python.exe",
    [string]$ModelPath = ".\qwen2.5-3b-instruct-q4_k_m.gguf",
    [string]$RuntimePath = ".\runtime\llama-cli.exe"
)

$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$distRoot = Join-Path $root "dist"
$packageRoot = Join-Path $distRoot "ChineseRewritePortable"
$builtAppRoot = Join-Path $distRoot "ChineseRewrite"

function Resolve-InputPath {
    param(
        [string]$Path
    )

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }

    return [System.IO.Path]::GetFullPath((Join-Path $root $Path))
}

$pythonPath = Resolve-InputPath $Python
$modelPathInput = Resolve-InputPath $ModelPath
$runtimePathInput = Resolve-InputPath $RuntimePath

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "Python executable not found: $Python"
}

if (-not (Test-Path -LiteralPath $modelPathInput)) {
    throw "Model file not found: $ModelPath"
}

if (-not (Test-Path -LiteralPath $runtimePathInput)) {
    throw "llama.cpp runtime not found: $RuntimePath"
}

Push-Location $root
try {
    & $pythonPath -m PyInstaller `
        --noconfirm `
        --clean `
        --windowed `
        --name ChineseRewrite `
        --paths src `
        src\chinese_rewrite\app.py

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }

    if (Test-Path -LiteralPath $packageRoot) {
        Remove-Item -LiteralPath $packageRoot -Recurse -Force
    }

    New-Item -ItemType Directory -Force -Path $packageRoot | Out-Null

    # PyInstaller onedir builds include support files next to the exe; copy the full tree.
    Get-ChildItem -LiteralPath $builtAppRoot -Force | Copy-Item -Destination $packageRoot -Recurse -Force

    New-Item -ItemType Directory -Force -Path `
        (Join-Path $packageRoot "models"), `
        (Join-Path $packageRoot "runtime"), `
        (Join-Path $packageRoot "config") | Out-Null

    Copy-Item -LiteralPath $modelPathInput -Destination (Join-Path $packageRoot "models\qwen2.5-3b-instruct-q4_k_m.gguf")
    Copy-Item -LiteralPath $runtimePathInput -Destination (Join-Path $packageRoot "runtime\llama-cli.exe")
    Copy-Item -LiteralPath (Join-Path $root "config\app.json") -Destination (Join-Path $packageRoot "config\app.json")

    Write-Host "Portable package created at $packageRoot"
}
finally {
    Pop-Location
}
