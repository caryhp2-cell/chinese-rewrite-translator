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
        self.concise_copy_button.clicked.connect(
            lambda: self.copy_output(self.concise_output)
        )

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
        layout.addWidget(
            self._build_output_box(
                "Concise English",
                self.concise_output,
                self.concise_copy_button,
            )
        )
        layout.addWidget(
            self._build_output_box(
                "Professional English",
                self.professional_output,
                self.professional_copy_button,
            )
        )
        return panel

    def _build_output_box(
        self, title: str, text_edit: QPlainTextEdit, copy_button: QPushButton
    ) -> QWidget:
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
