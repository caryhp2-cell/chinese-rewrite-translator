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
