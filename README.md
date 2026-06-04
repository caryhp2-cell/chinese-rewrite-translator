# Chinese Rewrite Translator

Portable offline Windows desktop app for rewriting Chinese text into two English versions:

- Concise English
- Professional English

The app is designed to run CPU-only with a local GGUF model through a bundled llama.cpp runtime. Model weights are not committed to this public repository.

## Local Model

Place the GGUF model in the app's local `models/` folder when running the application.

Current development model:

```text
qwen2.5-3b-instruct-q4_k_m.gguf
```

## Development

Create a virtual environment and install the project:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

Run tests:

```powershell
.\.venv\Scripts\python -m pytest -q
```

## Packaging

The portable release is assembled locally because model weights and runtime binaries are not committed.

Expected local inputs:

```text
qwen2.5-3b-instruct-q4_k_m.gguf
runtime/llama-cli.exe
```

Build the portable folder:

```powershell
.\scripts\package_portable.ps1
```

The output folder is:

```text
dist/ChineseRewritePortable/
```
