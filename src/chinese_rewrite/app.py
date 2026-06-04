from __future__ import annotations

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
