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
