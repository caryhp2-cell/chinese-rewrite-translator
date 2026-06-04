from __future__ import annotations

import sys
from pathlib import Path

from chinese_rewrite.core.models import AppConfig, PackageStatus, RewriteResult
from chinese_rewrite.core.paths import check_package_integrity, get_portable_root


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
