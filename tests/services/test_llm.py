from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from chinese_rewrite.core.models import AppConfig
from chinese_rewrite.services.llm import GenerationError, LlamaService


def test_llama_service_builds_expected_command(tmp_path: Path) -> None:
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


def test_llama_service_returns_parsed_result(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_run(*args, **kwargs):
        captured["command"] = args[0]
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout='{"concise": "Please confirm.", "professional": "Could you please confirm this?"}',
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    config = AppConfig.default()
    service = LlamaService(root=tmp_path, config=config)

    result = service.generate("prompt text")

    assert result.concise == "Please confirm."
    assert result.professional == "Could you please confirm this?"
    assert captured["command"] == service.build_command("prompt text")

    kwargs = captured["kwargs"]
    assert isinstance(kwargs, dict)
    assert kwargs["capture_output"] is True
    assert kwargs["text"] is True
    assert kwargs["encoding"] == "utf-8"
    assert kwargs["timeout"] == config.timeout_seconds
    assert kwargs["check"] is False


def test_llama_service_raises_generation_error_on_crash(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args[0], returncode=2, stdout="", stderr="bad runtime")

    monkeypatch.setattr(subprocess, "run", fake_run)
    service = LlamaService(root=tmp_path, config=AppConfig.default())

    with pytest.raises(GenerationError) as exc:
        service.generate("prompt text")

    assert str(exc.value) == "Generation failed: bad runtime"


def test_llama_service_raises_generation_error_on_crash_without_stderr(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args[0], returncode=2, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    service = LlamaService(root=tmp_path, config=AppConfig.default())

    with pytest.raises(GenerationError) as exc:
        service.generate("prompt text")

    assert str(exc.value) == "Generation failed: runtime exited with code 2"


def test_llama_service_raises_generation_error_on_launch_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def fake_run(*args, **kwargs):
        raise FileNotFoundError("missing runtime")

    monkeypatch.setattr(subprocess, "run", fake_run)
    service = LlamaService(root=tmp_path, config=AppConfig.default())

    with pytest.raises(GenerationError) as exc:
        service.generate("prompt text")

    assert str(exc.value) == "Could not start the local model runtime: missing runtime"


def test_llama_service_raises_generation_error_on_timeout(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=120)

    monkeypatch.setattr(subprocess, "run", fake_run)
    service = LlamaService(root=tmp_path, config=AppConfig.default())

    with pytest.raises(GenerationError) as exc:
        service.generate("prompt text")

    assert str(exc.value) == "Generation took too long. Please try again with shorter input."


def test_llama_service_raises_generation_error_on_empty_model_output(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args[0], returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    service = LlamaService(root=tmp_path, config=AppConfig.default())

    with pytest.raises(GenerationError) as exc:
        service.generate("prompt text")

    assert str(exc.value) == "Could not read the model response: no output received"
