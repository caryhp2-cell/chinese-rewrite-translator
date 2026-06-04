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
