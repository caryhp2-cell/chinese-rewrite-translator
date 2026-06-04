from __future__ import annotations

import os
import threading
import time
from collections.abc import Callable

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from chinese_rewrite.core.models import RewriteResult
from chinese_rewrite.ui.main_window import MainWindow


def wait_until(
    app: QApplication, predicate: Callable[[], bool], timeout_ms: int = 2000
) -> bool:
    deadline = time.monotonic() + (timeout_ms / 1000)
    while time.monotonic() < deadline:
        app.processEvents()
        if predicate():
            return True
        time.sleep(0.005)
    app.processEvents()
    return predicate()


@pytest.fixture()
def qt_app() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_empty_input_does_not_start_generation(qt_app: QApplication) -> None:
    calls: list[str] = []

    def generate(prompt: str) -> RewriteResult:
        calls.append(prompt)
        return RewriteResult(concise="unused", professional="unused")

    window = MainWindow(generate=generate)
    window.input_text.setPlainText("  ")

    window.start_generation()

    assert calls == []
    assert window.worker is None
    assert window.worker_thread is None
    assert window.rewrite_button.isEnabled()
    assert window.statusBar().currentMessage() == "Please enter Chinese text."


def test_successful_generation_populates_outputs(qt_app: QApplication) -> None:
    calls: list[str] = []

    def generate(prompt: str) -> RewriteResult:
        calls.append(prompt)
        return RewriteResult(
            concise="Hello.",
            professional="Hello, and thank you for reaching out.",
        )

    window = MainWindow(generate=generate)
    chinese_text = "\u4f60\u597d"
    window.input_text.setPlainText(chinese_text)

    window.start_generation()

    assert wait_until(qt_app, lambda: window.worker_thread is None)
    assert len(calls) == 1
    assert chinese_text in calls[0]
    assert window.concise_output.toPlainText() == "Hello."
    assert (
        window.professional_output.toPlainText()
        == "Hello, and thank you for reaching out."
    )
    assert window.rewrite_button.isEnabled()
    window.close()


def test_close_during_generation_is_ignored(qt_app: QApplication) -> None:
    worker_started = threading.Event()
    allow_finish = threading.Event()

    def generate(prompt: str) -> RewriteResult:
        worker_started.set()
        assert allow_finish.wait(timeout=2)
        return RewriteResult(concise="Done concise.", professional="Done professional.")

    window = MainWindow(generate=generate)
    window.input_text.setPlainText("\u7b49\u5f85\u4e00\u4e0b")
    window.show()

    window.start_generation()

    assert wait_until(
        qt_app,
        lambda: worker_started.is_set()
        and window.worker_thread is not None
        and window.worker_thread.isRunning(),
    )

    closed = window.close()
    qt_app.processEvents()

    assert closed is False
    assert window.isVisible()
    assert window.statusBar().currentMessage() == "Generation is still running."

    allow_finish.set()
    assert wait_until(qt_app, lambda: window.worker_thread is None)
    assert window.concise_output.toPlainText() == "Done concise."
    assert window.professional_output.toPlainText() == "Done professional."
    assert window.close() is True
