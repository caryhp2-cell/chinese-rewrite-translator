# Portable Chinese Rewrite Translator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a portable offline Windows desktop app that rewrites Chinese text into concise and professional English using a local GGUF model.

**Architecture:** Use a focused Python package with PySide6 for the desktop UI and a subprocess wrapper around a bundled llama.cpp CPU runtime. The executable resolves model and runtime paths relative to its own portable folder and fails fast with an incomplete-package screen when required files are missing.

**Tech Stack:** Python 3.12, PySide6, pytest, PyInstaller, llama.cpp GGUF runtime.

---

## File Structure

Create these files:

```text
pyproject.toml
src/chinese_rewrite/__init__.py
src/chinese_rewrite/app.py
src/chinese_rewrite/core/__init__.py
src/chinese_rewrite/core/models.py
src/chinese_rewrite/core/paths.py
src/chinese_rewrite/services/__init__.py
src/chinese_rewrite/services/prompts.py
src/chinese_rewrite/services/parser.py
src/chinese_rewrite/services/llm.py
src/chinese_rewrite/ui/__init__.py
src/chinese_rewrite/ui/main_window.py
tests/conftest.py
tests/core/test_paths.py
tests/services/test_prompts.py
tests/services/test_parser.py
tests/services/test_llm.py
scripts/package_portable.ps1
config/app.json
```

Modify these files:

```text
README.md
.gitignore
```

Keep these paths untracked:

```text
models/qwen2.5-3b-instruct-q4_k_m.gguf
runtime/llama-cli.exe
dist/
build/
```

## Task 1: Python Project Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `src/chinese_rewrite/__init__.py`
- Create: `src/chinese_rewrite/core/__init__.py`
- Create: `src/chinese_rewrite/services/__init__.py`
- Create: `src/chinese_rewrite/ui/__init__.py`
- Create: `tests/conftest.py`
- Modify: `README.md`

- [ ] **Step 1: Create packaging metadata**

Create `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "chinese-rewrite-translator"
version = "0.1.0"
description = "Portable offline Chinese-to-English rewrite desktop app"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
  "PySide6>=6.7,<7",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.2,<9",
  "pyinstaller>=6.8,<7",
]

[project.scripts]
chinese-rewrite = "chinese_rewrite.app:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Step 2: Create package marker files**

Create empty files:

```text
src/chinese_rewrite/__init__.py
src/chinese_rewrite/core/__init__.py
src/chinese_rewrite/services/__init__.py
src/chinese_rewrite/ui/__init__.py
```

- [ ] **Step 3: Add pytest import setup**

Create `tests/conftest.py`:

```python
from __future__ import annotations
```

- [ ] **Step 4: Update README with setup commands**

Append this section to `README.md`:

````markdown

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
````

- [ ] **Step 5: Verify package metadata**

Run:

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q
```

Expected:

```text
no tests ran
```

If pytest reports no tests with exit code 5, proceed after confirming imports will be covered by Task 2.

- [ ] **Step 6: Commit**

Run:

```powershell
git add pyproject.toml README.md src tests
git commit -m "chore: add Python project skeleton"
```

## Task 2: Core Data Models

**Files:**
- Create: `src/chinese_rewrite/core/models.py`
- Create: `tests/core/test_paths.py`

- [ ] **Step 1: Write failing tests for shared models**

Create `tests/core/test_paths.py` with the first model tests:

```python
from __future__ import annotations

from pathlib import Path

from chinese_rewrite.core.models import AppConfig, PackageStatus, RewriteResult


def test_rewrite_result_strips_surrounding_whitespace() -> None:
    result = RewriteResult(concise="  Clear reply.  ", professional="\nA polished reply.\n")

    assert result.concise == "Clear reply."
    assert result.professional == "A polished reply."


def test_app_config_defaults_to_expected_portable_paths() -> None:
    config = AppConfig.default()

    assert config.model_relative_path == Path("models/qwen2.5-3b-instruct-q4_k_m.gguf")
    assert config.runtime_relative_path == Path("runtime/llama-cli.exe")
    assert config.temperature == 0.2
    assert config.max_tokens == 512
    assert config.timeout_seconds == 120


def test_package_status_reports_ready_when_no_files_are_missing() -> None:
    status = PackageStatus(missing_files=[])

    assert status.is_ready is True
    assert status.message == ""


def test_package_status_message_lists_missing_files() -> None:
    status = PackageStatus(
        missing_files=[
            Path("models/qwen2.5-3b-instruct-q4_k_m.gguf"),
            Path("runtime/llama-cli.exe"),
        ]
    )

    assert status.is_ready is False
    assert status.message == (
        "This portable app folder is incomplete.\n"
        "Missing:\n"
        "- models/qwen2.5-3b-instruct-q4_k_m.gguf\n"
        "- runtime/llama-cli.exe\n"
        "Please restore the full ChineseRewritePortable folder."
    )
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
python -m pytest tests/core/test_paths.py -q
```

Expected: FAIL because `chinese_rewrite.core.models` does not exist.

- [ ] **Step 3: Implement shared models**

Create `src/chinese_rewrite/core/models.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RewriteResult:
    concise: str
    professional: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "concise", self.concise.strip())
        object.__setattr__(self, "professional", self.professional.strip())


@dataclass(frozen=True)
class AppConfig:
    model_relative_path: Path
    runtime_relative_path: Path
    temperature: float
    max_tokens: int
    timeout_seconds: int

    @classmethod
    def default(cls) -> "AppConfig":
        return cls(
            model_relative_path=Path("models/qwen2.5-3b-instruct-q4_k_m.gguf"),
            runtime_relative_path=Path("runtime/llama-cli.exe"),
            temperature=0.2,
            max_tokens=512,
            timeout_seconds=120,
        )


@dataclass(frozen=True)
class PackageStatus:
    missing_files: list[Path]

    @property
    def is_ready(self) -> bool:
        return not self.missing_files

    @property
    def message(self) -> str:
        if self.is_ready:
            return ""

        missing = "\n".join(f"- {path.as_posix()}" for path in self.missing_files)
        return (
            "This portable app folder is incomplete.\n"
            "Missing:\n"
            f"{missing}\n"
            "Please restore the full ChineseRewritePortable folder."
        )
```

- [ ] **Step 4: Run tests**

Run:

```powershell
python -m pytest tests/core/test_paths.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/chinese_rewrite/core/models.py tests/core/test_paths.py
git commit -m "feat: add core app models"
```

## Task 3: Portable Path Resolution And Integrity Check

**Files:**
- Create: `src/chinese_rewrite/core/paths.py`
- Modify: `tests/core/test_paths.py`

- [ ] **Step 1: Extend path tests**

Append to `tests/core/test_paths.py`:

```python
import sys

from chinese_rewrite.core.paths import check_package_integrity, get_portable_root


def test_get_portable_root_uses_current_file_tree_when_not_frozen(monkeypatch, tmp_path) -> None:
    fake_paths_file = tmp_path / "repo" / "src" / "chinese_rewrite" / "core" / "paths.py"
    fake_paths_file.parent.mkdir(parents=True)
    fake_paths_file.write_text("", encoding="utf-8")

    monkeypatch.setattr(sys, "frozen", False, raising=False)

    root = get_portable_root(paths_file=fake_paths_file)

    assert root == tmp_path / "repo"


def test_get_portable_root_uses_executable_parent_when_frozen(monkeypatch, tmp_path) -> None:
    exe_path = tmp_path / "ChineseRewritePortable" / "ChineseRewrite.exe"
    exe_path.parent.mkdir()
    exe_path.write_text("", encoding="utf-8")

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(exe_path))

    root = get_portable_root()

    assert root == exe_path.parent


def test_check_package_integrity_passes_when_model_and_runtime_exist(tmp_path) -> None:
    config = AppConfig.default()
    model = tmp_path / config.model_relative_path
    runtime = tmp_path / config.runtime_relative_path
    model.parent.mkdir(parents=True)
    runtime.parent.mkdir(parents=True)
    model.write_bytes(b"model")
    runtime.write_bytes(b"runtime")

    status = check_package_integrity(tmp_path, config)

    assert status.is_ready is True
    assert status.missing_files == []


def test_check_package_integrity_reports_missing_relative_paths(tmp_path) -> None:
    config = AppConfig.default()

    status = check_package_integrity(tmp_path, config)

    assert status.is_ready is False
    assert status.missing_files == [
        Path("models/qwen2.5-3b-instruct-q4_k_m.gguf"),
        Path("runtime/llama-cli.exe"),
    ]
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
python -m pytest tests/core/test_paths.py -q
```

Expected: FAIL because `chinese_rewrite.core.paths` does not exist.

- [ ] **Step 3: Implement path helpers**

Create `src/chinese_rewrite/core/paths.py`:

```python
from __future__ import annotations

import sys
from pathlib import Path

from chinese_rewrite.core.models import AppConfig, PackageStatus


def get_portable_root(paths_file: Path | None = None) -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    current_file = (paths_file or Path(__file__)).resolve()
    return current_file.parents[3]


def check_package_integrity(root: Path, config: AppConfig) -> PackageStatus:
    required = [
        config.model_relative_path,
        config.runtime_relative_path,
    ]
    missing = [relative for relative in required if not (root / relative).is_file()]
    return PackageStatus(missing_files=missing)
```

- [ ] **Step 4: Run tests**

Run:

```powershell
python -m pytest tests/core/test_paths.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/chinese_rewrite/core/paths.py tests/core/test_paths.py
git commit -m "feat: add portable integrity checks"
```

## Task 4: Prompt Builder

**Files:**
- Create: `src/chinese_rewrite/services/prompts.py`
- Create: `tests/services/test_prompts.py`

- [ ] **Step 1: Write failing prompt tests**

Create `tests/services/test_prompts.py`:

```python
from __future__ import annotations

from chinese_rewrite.services.prompts import build_rewrite_prompt


def test_build_rewrite_prompt_includes_json_contract_and_input() -> None:
    prompt = build_rewrite_prompt("我們需要在週五前完成報告。")

    assert "Return valid JSON only." in prompt
    assert '"concise"' in prompt
    assert '"professional"' in prompt
    assert "Preserve the original meaning. Do not add facts." in prompt
    assert "我們需要在週五前完成報告。" in prompt


def test_build_rewrite_prompt_rejects_empty_input() -> None:
    try:
        build_rewrite_prompt("  \n ")
    except ValueError as exc:
        assert str(exc) == "Chinese input is empty."
    else:
        raise AssertionError("Expected ValueError for empty input")


def test_build_rewrite_prompt_strips_outer_whitespace() -> None:
    prompt = build_rewrite_prompt("  請協助確認付款狀態。  ")

    assert "Chinese input:\n請協助確認付款狀態。" in prompt
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
python -m pytest tests/services/test_prompts.py -q
```

Expected: FAIL because `build_rewrite_prompt` is not defined.

- [ ] **Step 3: Implement prompt builder**

Create `src/chinese_rewrite/services/prompts.py`:

```python
from __future__ import annotations


def build_rewrite_prompt(chinese_text: str) -> str:
    cleaned = chinese_text.strip()
    if not cleaned:
        raise ValueError("Chinese input is empty.")

    return (
        "Translate and rewrite the Chinese input into English.\n"
        "Return exactly two versions:\n"
        '1. "concise": brief, natural, clear.\n'
        '2. "professional": polished, business-appropriate, complete.\n'
        "Preserve the original meaning. Do not add facts.\n"
        "Return valid JSON only.\n\n"
        "Expected JSON shape:\n"
        '{\n'
        '  "concise": "Short, clear English version.",\n'
        '  "professional": "Polished professional English version."\n'
        '}\n\n'
        "Chinese input:\n"
        f"{cleaned}"
    )
```

- [ ] **Step 4: Run tests**

Run:

```powershell
python -m pytest tests/services/test_prompts.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/chinese_rewrite/services/prompts.py tests/services/test_prompts.py
git commit -m "feat: add rewrite prompt builder"
```

## Task 5: Model Output Parser

**Files:**
- Create: `src/chinese_rewrite/services/parser.py`
- Create: `tests/services/test_parser.py`

- [ ] **Step 1: Write failing parser tests**

Create `tests/services/test_parser.py`:

```python
from __future__ import annotations

import pytest

from chinese_rewrite.services.parser import ModelOutputParseError, parse_rewrite_output


def test_parse_rewrite_output_accepts_strict_json() -> None:
    result = parse_rewrite_output(
        '{"concise": "Please confirm payment.", "professional": "Could you please confirm the payment status?"}'
    )

    assert result.concise == "Please confirm payment."
    assert result.professional == "Could you please confirm the payment status?"


def test_parse_rewrite_output_extracts_json_inside_extra_text() -> None:
    result = parse_rewrite_output(
        'Here is the result:\n{"concise":"Done by Friday.","professional":"We will complete the report by Friday."}\nThanks.'
    )

    assert result.concise == "Done by Friday."
    assert result.professional == "We will complete the report by Friday."


def test_parse_rewrite_output_uses_label_fallback() -> None:
    result = parse_rewrite_output(
        "Concise: Please reply today.\nProfessional: Could you please respond by the end of today?"
    )

    assert result.concise == "Please reply today."
    assert result.professional == "Could you please respond by the end of today?"


def test_parse_rewrite_output_rejects_missing_professional() -> None:
    with pytest.raises(ModelOutputParseError) as exc:
        parse_rewrite_output('{"concise": "Please reply today."}')

    assert str(exc.value) == "Model output did not contain both rewrite fields."


def test_parse_rewrite_output_rejects_empty_fields() -> None:
    with pytest.raises(ModelOutputParseError):
        parse_rewrite_output('{"concise": " ", "professional": "Polished text."}')
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
python -m pytest tests/services/test_parser.py -q
```

Expected: FAIL because `chinese_rewrite.services.parser` does not exist.

- [ ] **Step 3: Implement parser**

Create `src/chinese_rewrite/services/parser.py`:

```python
from __future__ import annotations

import json
import re
from typing import Any

from chinese_rewrite.core.models import RewriteResult


class ModelOutputParseError(ValueError):
    pass


def parse_rewrite_output(raw_output: str) -> RewriteResult:
    for candidate in _json_candidates(raw_output):
        parsed = _parse_json_candidate(candidate)
        if parsed is not None:
            return parsed

    fallback = _parse_label_fallback(raw_output)
    if fallback is not None:
        return fallback

    raise ModelOutputParseError("Model output did not contain both rewrite fields.")


def _json_candidates(raw_output: str) -> list[str]:
    stripped = raw_output.strip()
    candidates = [stripped]

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidates.append(stripped[start : end + 1])

    return candidates


def _parse_json_candidate(candidate: str) -> RewriteResult | None:
    try:
        payload: Any = json.loads(candidate)
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, dict):
        return None

    concise = payload.get("concise")
    professional = payload.get("professional")
    if not isinstance(concise, str) or not isinstance(professional, str):
        return None

    result = RewriteResult(concise=concise, professional=professional)
    if not result.concise or not result.professional:
        raise ModelOutputParseError("Model output did not contain both rewrite fields.")

    return result


def _parse_label_fallback(raw_output: str) -> RewriteResult | None:
    match = re.search(
        r"Concise:\s*(?P<concise>.+?)\s*Professional:\s*(?P<professional>.+)\s*$",
        raw_output,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None

    result = RewriteResult(
        concise=match.group("concise"),
        professional=match.group("professional"),
    )
    if not result.concise or not result.professional:
        return None

    return result
```

- [ ] **Step 4: Run tests**

Run:

```powershell
python -m pytest tests/services/test_parser.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/chinese_rewrite/services/parser.py tests/services/test_parser.py
git commit -m "feat: parse rewrite model output"
```

## Task 6: llama.cpp Subprocess Service

**Files:**
- Create: `src/chinese_rewrite/services/llm.py`
- Create: `tests/services/test_llm.py`

- [ ] **Step 1: Write failing service tests**

Create `tests/services/test_llm.py`:

```python
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from chinese_rewrite.core.models import AppConfig
from chinese_rewrite.services.llm import GenerationError, LlamaService


def test_llama_service_builds_expected_command(tmp_path) -> None:
    config = AppConfig.default()
    service = LlamaService(root=tmp_path, config=config)

    command = service.build_command("prompt text")

    assert command == [
        str(tmp_path / "runtime/llama-cli.exe"),
        "-m",
        str(tmp_path / "models/qwen2.5-3b-instruct-q4_k_m.gguf"),
        "-p",
        "prompt text",
        "--temp",
        "0.2",
        "-n",
        "512",
        "--no-display-prompt",
    ]


def test_llama_service_returns_parsed_result(monkeypatch, tmp_path) -> None:
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout='{"concise": "Please confirm.", "professional": "Could you please confirm this?"}',
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    service = LlamaService(root=tmp_path, config=AppConfig.default())

    result = service.generate("prompt text")

    assert result.concise == "Please confirm."
    assert result.professional == "Could you please confirm this?"


def test_llama_service_raises_generation_error_on_crash(monkeypatch, tmp_path) -> None:
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args[0], returncode=2, stdout="", stderr="bad runtime")

    monkeypatch.setattr(subprocess, "run", fake_run)
    service = LlamaService(root=tmp_path, config=AppConfig.default())

    with pytest.raises(GenerationError) as exc:
        service.generate("prompt text")

    assert str(exc.value) == "Generation failed: bad runtime"


def test_llama_service_raises_generation_error_on_timeout(monkeypatch, tmp_path) -> None:
    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=120)

    monkeypatch.setattr(subprocess, "run", fake_run)
    service = LlamaService(root=tmp_path, config=AppConfig.default())

    with pytest.raises(GenerationError) as exc:
        service.generate("prompt text")

    assert str(exc.value) == "Generation took too long. Please try again with shorter input."
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
python -m pytest tests/services/test_llm.py -q
```

Expected: FAIL because `chinese_rewrite.services.llm` does not exist.

- [ ] **Step 3: Implement service**

Create `src/chinese_rewrite/services/llm.py`:

```python
from __future__ import annotations

import subprocess
from pathlib import Path

from chinese_rewrite.core.models import AppConfig, RewriteResult
from chinese_rewrite.services.parser import ModelOutputParseError, parse_rewrite_output


class GenerationError(RuntimeError):
    pass


class LlamaService:
    def __init__(self, root: Path, config: AppConfig) -> None:
        self.root = root
        self.config = config

    @property
    def runtime_path(self) -> Path:
        return self.root / self.config.runtime_relative_path

    @property
    def model_path(self) -> Path:
        return self.root / self.config.model_relative_path

    def build_command(self, prompt: str) -> list[str]:
        return [
            str(self.runtime_path),
            "-m",
            str(self.model_path),
            "-p",
            prompt,
            "--temp",
            str(self.config.temperature),
            "-n",
            str(self.config.max_tokens),
            "--no-display-prompt",
        ]

    def generate(self, prompt: str) -> RewriteResult:
        try:
            completed = subprocess.run(
                self.build_command(prompt),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=self.config.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise GenerationError(
                "Generation took too long. Please try again with shorter input."
            ) from exc

        if completed.returncode != 0:
            details = completed.stderr.strip() or f"runtime exited with code {completed.returncode}"
            raise GenerationError(f"Generation failed: {details}")

        try:
            return parse_rewrite_output(completed.stdout)
        except ModelOutputParseError as exc:
            preview = completed.stdout.strip().replace("\n", " ")[:240]
            raise GenerationError(f"Could not read the model response: {preview}") from exc
```

- [ ] **Step 4: Run tests**

Run:

```powershell
python -m pytest tests/services/test_llm.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/chinese_rewrite/services/llm.py tests/services/test_llm.py
git commit -m "feat: add llama subprocess service"
```

## Task 7: PySide6 Workbench UI

**Files:**
- Create: `src/chinese_rewrite/ui/main_window.py`
- Create: `src/chinese_rewrite/app.py`

- [ ] **Step 1: Create the main window**

Create `src/chinese_rewrite/ui/main_window.py`:

```python
from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from chinese_rewrite.core.models import RewriteResult
from chinese_rewrite.services.prompts import build_rewrite_prompt


GenerateFn = Callable[[str], RewriteResult]


class RewriteWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, chinese_text: str, generate: GenerateFn) -> None:
        super().__init__()
        self.chinese_text = chinese_text
        self.generate = generate

    @Slot()
    def run(self) -> None:
        try:
            prompt = build_rewrite_prompt(self.chinese_text)
            self.finished.emit(self.generate(prompt))
        except Exception as exc:
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self, generate: GenerateFn) -> None:
        super().__init__()
        self.generate = generate
        self.worker_thread: QThread | None = None
        self.worker: RewriteWorker | None = None

        self.setWindowTitle("Chinese Rewrite Translator")
        self.resize(1040, 680)

        self.input_text = QPlainTextEdit()
        self.input_text.setPlaceholderText("Enter Chinese text...")

        self.rewrite_button = QPushButton("Translate / Rewrite")
        self.rewrite_button.clicked.connect(self.start_generation)

        self.concise_output = QPlainTextEdit()
        self.concise_output.setReadOnly(True)

        self.professional_output = QPlainTextEdit()
        self.professional_output.setReadOnly(True)

        self.concise_copy_button = QPushButton("Copy")
        self.concise_copy_button.clicked.connect(lambda: self.copy_output(self.concise_output))

        self.professional_copy_button = QPushButton("Copy")
        self.professional_copy_button.clicked.connect(
            lambda: self.copy_output(self.professional_output)
        )

        self.setCentralWidget(self._build_layout())
        self.setStatusBar(QStatusBar())

    def _build_layout(self) -> QWidget:
        root = QWidget()
        root_layout = QHBoxLayout(root)

        splitter = QSplitter()
        splitter.addWidget(self._build_input_panel())
        splitter.addWidget(self._build_output_panel())
        splitter.setSizes([500, 540])

        root_layout.addWidget(splitter)
        return root

    def _build_input_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Chinese Input"))
        layout.addWidget(self.input_text)
        layout.addWidget(self.rewrite_button)
        return panel

    def _build_output_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(self._build_output_box("Concise English", self.concise_output, self.concise_copy_button))
        layout.addWidget(
            self._build_output_box(
                "Professional English",
                self.professional_output,
                self.professional_copy_button,
            )
        )
        return panel

    def _build_output_box(self, title: str, text_edit: QPlainTextEdit, copy_button: QPushButton) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        header = QHBoxLayout()
        header.addWidget(QLabel(title))
        header.addStretch()
        header.addWidget(copy_button)
        layout.addLayout(header)
        layout.addWidget(text_edit)
        return panel

    @Slot()
    def start_generation(self) -> None:
        chinese_text = self.input_text.toPlainText().strip()
        if not chinese_text:
            self.statusBar().showMessage("Please enter Chinese text.", 5000)
            return

        self.rewrite_button.setEnabled(False)
        self.concise_output.setPlainText("Generating...")
        self.professional_output.setPlainText("Generating...")
        self.statusBar().showMessage("Generating offline rewrite...")

        self.worker_thread = QThread()
        self.worker = RewriteWorker(chinese_text, self.generate)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.failed.connect(self.on_generation_failed)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.failed.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    @Slot(object)
    def on_generation_finished(self, result: RewriteResult) -> None:
        self.concise_output.setPlainText(result.concise)
        self.professional_output.setPlainText(result.professional)
        self.rewrite_button.setEnabled(True)
        self.statusBar().showMessage("Done.", 3000)
        self.worker = None
        self.worker_thread = None

    @Slot(str)
    def on_generation_failed(self, message: str) -> None:
        self.concise_output.clear()
        self.professional_output.clear()
        self.rewrite_button.setEnabled(True)
        self.statusBar().showMessage("Generation failed.", 5000)
        QMessageBox.warning(self, "Generation failed", message)
        self.worker = None
        self.worker_thread = None

    def copy_output(self, text_edit: QPlainTextEdit) -> None:
        QGuiApplication.clipboard().setText(text_edit.toPlainText())
        self.statusBar().showMessage("Copied.", 2000)


def run_main_window(generate: GenerateFn) -> int:
    app = QApplication.instance() or QApplication([])
    window = MainWindow(generate=generate)
    window.show()
    return app.exec()
```

- [ ] **Step 2: Create app entrypoint with integrity screen**

Create `src/chinese_rewrite/app.py`:

```python
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from chinese_rewrite.core.models import AppConfig
from chinese_rewrite.core.paths import check_package_integrity, get_portable_root
from chinese_rewrite.services.llm import LlamaService
from chinese_rewrite.ui.main_window import run_main_window


def main() -> int:
    config = AppConfig.default()
    root = get_portable_root()
    status = check_package_integrity(root, config)

    if not status.is_ready:
        app = QApplication.instance() or QApplication([])
        QMessageBox.critical(None, "Incomplete portable folder", status.message)
        return 1

    service = LlamaService(root=root, config=config)
    return run_main_window(service.generate)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3: Run existing tests**

Run:

```powershell
python -m pytest -q
```

Expected: PASS.

- [ ] **Step 4: Manual UI smoke test without model**

Run:

```powershell
python -m chinese_rewrite.app
```

Expected with current repo state: an incomplete portable folder dialog appears listing:

```text
models/qwen2.5-3b-instruct-q4_k_m.gguf
runtime/llama-cli.exe
```

The dialog is correct because `models/` and `runtime/` are ignored local release inputs.

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/chinese_rewrite/ui/main_window.py src/chinese_rewrite/app.py
git commit -m "feat: add desktop workbench UI"
```

## Task 8: Default Config And Packaging Script

**Files:**
- Create: `config/app.json`
- Create: `scripts/package_portable.ps1`
- Modify: `.gitignore`
- Modify: `README.md`

- [ ] **Step 1: Create default config**

Create `config/app.json`:

```json
{
  "model": "models/qwen2.5-3b-instruct-q4_k_m.gguf",
  "runtime": "runtime/llama-cli.exe",
  "temperature": 0.2,
  "max_tokens": 512,
  "timeout_seconds": 120
}
```

- [ ] **Step 2: Create portable packaging script**

Create `scripts/package_portable.ps1`:

```powershell
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
```

- [ ] **Step 3: Confirm ignored build outputs**

Ensure `.gitignore` contains these lines:

```gitignore
build/
dist/
*.spec
runtime/
models/
```

- [ ] **Step 4: Update README packaging section**

Append this section to `README.md`:

````markdown

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
````

- [ ] **Step 5: Run tests**

Run:

```powershell
python -m pytest -q
```

Expected: PASS.

- [ ] **Step 6: Run packaging script error path**

Run:

```powershell
.\scripts\package_portable.ps1 -RuntimePath ".\runtime\missing-llama-cli.exe"
```

Expected: script stops with:

```text
llama.cpp runtime not found: .\runtime\missing-llama-cli.exe
```

- [ ] **Step 7: Commit**

Run:

```powershell
git add config/app.json scripts/package_portable.ps1 README.md .gitignore
git commit -m "feat: add portable packaging script"
```

## Task 9: Local Runtime Smoke Test

**Files:**
- Create: `tests/services/test_llm_smoke.py`

- [ ] **Step 1: Create opt-in smoke test**

Create `tests/services/test_llm_smoke.py`:

```python
from __future__ import annotations

import os
from pathlib import Path

import pytest

from chinese_rewrite.core.models import AppConfig
from chinese_rewrite.services.llm import LlamaService
from chinese_rewrite.services.prompts import build_rewrite_prompt


@pytest.mark.skipif(
    os.environ.get("RUN_LOCAL_LLM_SMOKE") != "1",
    reason="Set RUN_LOCAL_LLM_SMOKE=1 to run the local GGUF smoke test.",
)
def test_local_llama_runtime_returns_two_rewrite_fields() -> None:
    root = Path.cwd()
    service = LlamaService(root=root, config=AppConfig.default())
    prompt = build_rewrite_prompt("請在週五前回覆我是否可以參加會議。")

    result = service.generate(prompt)

    assert result.concise
    assert result.professional
    assert result.concise != result.professional
```

- [ ] **Step 2: Run normal tests**

Run:

```powershell
python -m pytest -q
```

Expected: PASS with one skipped smoke test.

- [ ] **Step 3: Prepare local smoke paths**

If the GGUF file remains in the repo root, create a local ignored `models/` folder and copy the model there:

```powershell
New-Item -ItemType Directory -Force -Path .\models | Out-Null
Copy-Item .\qwen2.5-3b-instruct-q4_k_m.gguf .\models\qwen2.5-3b-instruct-q4_k_m.gguf
```

Place `llama-cli.exe` at:

```text
runtime/llama-cli.exe
```

- [ ] **Step 4: Run opt-in smoke test**

Run:

```powershell
$env:RUN_LOCAL_LLM_SMOKE = "1"
python -m pytest tests/services/test_llm_smoke.py -q
Remove-Item Env:\RUN_LOCAL_LLM_SMOKE
```

Expected: PASS if the local llama.cpp runtime is present and compatible. If the runtime is absent, stop and obtain the Windows CPU `llama-cli.exe` before continuing.

- [ ] **Step 5: Commit**

Run:

```powershell
git add tests/services/test_llm_smoke.py
git commit -m "test: add opt-in local llm smoke test"
```

## Task 10: Final Verification And Push

**Files:**
- Modify: no files unless verification exposes a defect.

- [ ] **Step 1: Run full unit test suite**

Run:

```powershell
python -m pytest -q
```

Expected: all unit tests pass, smoke test skipped unless `RUN_LOCAL_LLM_SMOKE=1`.

- [ ] **Step 2: Verify git ignores the model**

Run:

```powershell
git status --short --ignored
```

Expected includes ignored model/cache entries and no staged model file:

```text
!! .cache/
!! .superpowers/
!! models/
!! qwen2.5-3b-instruct-q4_k_m.gguf
```

- [ ] **Step 3: Push commits**

Run:

```powershell
git push
```

Expected: `main` pushes to `origin/main`.

- [ ] **Step 4: Manual acceptance check**

Run:

```powershell
python -m chinese_rewrite.app
```

Expected when package inputs are missing from portable paths: incomplete-package dialog.

With `models/qwen2.5-3b-instruct-q4_k_m.gguf` and `runtime/llama-cli.exe` present:

1. The Workbench window opens.
2. Enter `請在週五前回覆我是否可以參加會議。`
3. Click `Translate / Rewrite`.
4. Concise English and Professional English fields both populate.
5. Each Copy button writes its field text to the clipboard.
