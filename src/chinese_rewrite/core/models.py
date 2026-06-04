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
