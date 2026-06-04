# Portable Chinese Rewrite Translator Design

## Goal

Build a portable offline Windows desktop app that rewrites Chinese input into two English outputs:

- Concise English
- Professional English

The app is intended for Windows 10/11 64-bit, CPU-only use. The released app should run from a self-contained folder that can be copied to a USB drive and launched on another compatible Windows computer.

## Decisions

- The app runs fully offline.
- The first version uses the local Qwen2.5 3B Instruct GGUF model.
- The app uses CPU-only llama.cpp runtime binaries bundled inside the portable folder.
- The UI uses a Workbench layout.
- Translation is triggered manually with a button.
- Each output field has a Copy button.
- The first version does not save history.
- The first version does not support cloud APIs.
- The first version does not include automatic generation while typing.

## Portable Package

The released folder has this structure:

```text
ChineseRewritePortable/
  ChineseRewrite.exe
  models/
    qwen2.5-3b-instruct-q4_k_m.gguf
  runtime/
    llama-cli.exe
  config/
    app.json
```

The executable treats its own folder as the portable root. All paths are resolved relative to that root. The user should not need to configure model or runtime paths.

## Repository Layout

The repository does not commit large model weights or runtime binaries. Development-only local copies live in ignored folders.

```text
repo/
  src/
  tests/
  docs/
  README.md
  models/    # ignored
  runtime/   # ignored
```

Suggested app modules:

```text
src/chinese_rewrite/
  app.py
  ui/main_window.py
  services/llm.py
  services/prompts.py
  services/parser.py
  core/paths.py
  core/models.py
```

Responsibilities:

- `app.py`: application entrypoint and startup orchestration.
- `ui/main_window.py`: PySide6 Workbench window and user interactions.
- `services/llm.py`: llama.cpp subprocess wrapper.
- `services/prompts.py`: prompt construction.
- `services/parser.py`: JSON and fallback output parsing.
- `core/paths.py`: portable root detection and package integrity checks.
- `core/models.py`: simple data classes such as `RewriteResult` and `AppConfig`.

## UI Design

The app uses a Workbench layout:

- Left side: Chinese input text area and the Translate/Rewrite button.
- Right side: two output panels.
- Top output: Concise English.
- Bottom output: Professional English.
- Each output panel includes a Copy button.

When generation starts:

- Disable the Translate/Rewrite button.
- Show a loading state in the output area.
- Run inference in a background worker so the window stays responsive.

When generation finishes:

- Fill both output fields at the same time.
- Re-enable the Translate/Rewrite button.

If the input is empty:

- Do not call the model.
- Show a lightweight validation message in the UI.

## Startup Integrity Check

Because this is a portable folder app, missing model or runtime files are treated as package integrity failures, not normal user configuration tasks.

At startup the app checks for:

- `models/qwen2.5-3b-instruct-q4_k_m.gguf`
- `runtime/llama-cli.exe`

If required files are present, the app enters the normal Workbench UI.

If required files are missing, the app shows an incomplete-package screen such as:

```text
This portable app folder is incomplete.
Missing: models/qwen2.5-3b-instruct-q4_k_m.gguf
Please restore the full ChineseRewritePortable folder.
```

The first version does not ask the user to browse for a model or runtime path.

## Model Invocation

The first version uses a single llama.cpp call per request. The prompt asks the model to return both outputs in one JSON object:

```json
{
  "concise": "Short, clear English version.",
  "professional": "Polished professional English version."
}
```

Single-call generation is preferred because it is faster on CPU-only machines and helps keep both outputs semantically aligned.

The model call should run with conservative defaults:

- Low temperature for stable rewriting.
- A bounded max token count suitable for short to medium business text.
- A timeout so subprocess failures do not hang the UI forever.

Exact default values can be tuned during implementation after local smoke tests.

## Prompt Design

The prompt instructs the model to preserve meaning and avoid adding facts:

```text
Translate and rewrite the Chinese input into English.
Return exactly two versions:
1. concise: brief, natural, clear.
2. professional: polished, business-appropriate, complete.
Preserve the original meaning. Do not add facts.
Return valid JSON only.
```

The Chinese input is inserted after this instruction. The prompt builder owns formatting and escaping so UI code does not assemble prompts directly.

## Parsing

The parser first attempts strict JSON parsing. It expects two string fields:

- `concise`
- `professional`

If strict parsing fails, it attempts a conservative fallback extraction from the raw model output. If fallback extraction also fails, the UI displays a retryable error.

The parser should not silently invent missing content.

## Error Handling

Errors are surfaced in user-friendly language:

- Empty input: ask the user to enter Chinese text.
- Incomplete portable folder: show the missing file and ask the user to restore the full folder.
- Runtime crash: show that generation failed and can be retried.
- Timeout: show that generation took too long and can be retried.
- Parse failure: show that the model response could not be read, with a short raw-output summary for debugging.

The app should not close because of generation errors.

## Packaging

Packaging creates the portable release folder:

1. Build `ChineseRewrite.exe` with PyInstaller.
2. Copy the GGUF model into `dist/ChineseRewritePortable/models/`.
3. Copy the llama.cpp CPU runtime into `dist/ChineseRewritePortable/runtime/`.
4. Copy default config into `dist/ChineseRewritePortable/config/app.json`.
5. Run a smoke test against the packaged folder.

The public repository excludes large binaries and local build artifacts.

## Testing

Unit tests:

- Portable root detection.
- Startup integrity check.
- Prompt builder output.
- JSON parser.
- Fallback parser.

Smoke test:

- Run one Chinese input through the local llama.cpp runtime.
- Verify the app receives both `concise` and `professional` fields.

Manual UI test:

- Launch the app.
- Enter Chinese text.
- Click Translate/Rewrite.
- Confirm both outputs appear.
- Confirm each Copy button copies the expected text.

Packaged test:

- Build `ChineseRewritePortable`.
- Launch `ChineseRewrite.exe` from the packaged folder.
- Confirm startup integrity passes.
- Move or remove one required file and confirm the incomplete-package screen appears.

## Explicitly Out Of Scope For MVP

- Cloud translation or rewriting APIs.
- GPU acceleration.
- Translation history.
- Auto-generate while typing.
- Output editing.
- Per-output regeneration.
- User-selectable model path.
- Cross-platform macOS or Linux support.
