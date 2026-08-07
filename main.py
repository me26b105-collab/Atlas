"""
Atlas CAE Platform Interface
Application Entry Point.
"""

import sys
from PySide6.QtWidgets import QApplication

from components.main_window import AtlasMainWindow
from styles import apply_dark_theme


def main() -> None:
    app = QApplication(sys.argv)
    app.setOrganizationName("Atlas Engineering")
    app.setApplicationName("Atlas")

    # Apply Atlas dark design system styling
    apply_dark_theme(app)

    # Instantiate and display the interface
    window = AtlasMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
