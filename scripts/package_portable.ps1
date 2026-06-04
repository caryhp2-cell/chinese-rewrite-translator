param(
    [string]$Python = ".\.venv\Scripts\python.exe",
    [string]$ModelPath = ".\qwen2.5-3b-instruct-q4_k_m.gguf",
    [string]$RuntimePath = ".\runtime\llama-cli.exe"
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$distRoot = Join-Path $root "dist"
$packageRoot = Join-Path $distRoot "ChineseRewritePortable"

if (-not (Test-Path $Python)) {
    throw "Python executable not found: $Python"
}

if (-not (Test-Path $ModelPath)) {
    throw "Model file not found: $ModelPath"
}

if (-not (Test-Path $RuntimePath)) {
    throw "llama.cpp runtime not found: $RuntimePath"
}

Push-Location $root
try {
    & $Python -m PyInstaller `
        --noconfirm `
        --clean `
        --windowed `
        --name ChineseRewrite `
        --paths src `
        src\chinese_rewrite\app.py

    if (Test-Path $packageRoot) {
        Remove-Item -LiteralPath $packageRoot -Recurse -Force
    }

    New-Item -ItemType Directory -Force -Path `
        (Join-Path $packageRoot "models"), `
        (Join-Path $packageRoot "runtime"), `
        (Join-Path $packageRoot "config") | Out-Null

    Copy-Item -LiteralPath (Join-Path $distRoot "ChineseRewrite\ChineseRewrite.exe") -Destination $packageRoot
    Copy-Item -LiteralPath $ModelPath -Destination (Join-Path $packageRoot "models\qwen2.5-3b-instruct-q4_k_m.gguf")
    Copy-Item -LiteralPath $RuntimePath -Destination (Join-Path $packageRoot "runtime\llama-cli.exe")
    Copy-Item -LiteralPath (Join-Path $root "config\app.json") -Destination (Join-Path $packageRoot "config\app.json")

    Write-Host "Portable package created at $packageRoot"
}
finally {
    Pop-Location
}
