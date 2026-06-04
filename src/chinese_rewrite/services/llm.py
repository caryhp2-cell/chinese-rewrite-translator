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
        except OSError as exc:
            raise GenerationError(f"Could not start the local model runtime: {exc}") from exc

        if completed.returncode != 0:
            details = completed.stderr.strip() or f"runtime exited with code {completed.returncode}"
            raise GenerationError(f"Generation failed: {details}")

        try:
            return parse_rewrite_output(completed.stdout)
        except ModelOutputParseError as exc:
            preview = completed.stdout.strip().replace("\n", " ")[:240] or "no output received"
            raise GenerationError(f"Could not read the model response: {preview}") from exc
