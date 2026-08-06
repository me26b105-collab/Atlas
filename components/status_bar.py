"""Atlas Status Bar Component."""

from PySide6.QtWidgets import QLabel, QStatusBar


class AtlasStatusBar(QStatusBar):
    """Bottom status bar displaying operational state info."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setSizeGripEnabled(False)

        self.status_label = QLabel("Ready", self)
        self.status_label.setStyleSheet(
            "padding-left: 8px; color: #a0a5b0;"
        )

        self.addWidget(self.status_label, 1)

    def set_message(self, message: str) -> None:
        """Update the status bar message."""

        self.status_label.setText(message)