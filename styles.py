"""
Atlas UI Design System & Stylesheet Configuration.
Provides a modern dark theme suitable for high-density engineering CAD/CAE tools.
"""

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


def apply_dark_theme(app: QApplication) -> None:
    """Configures the application-wide dark palette and QSS stylesheet."""
    app.setStyle("Fusion")

    # Base Dark Palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(32, 34, 38))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 224, 230))
    palette.setColor(QPalette.ColorRole.Base, QColor(24, 25, 28))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(32, 34, 38))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(220, 224, 230))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(32, 34, 38))
    palette.setColor(QPalette.ColorRole.Text, QColor(220, 224, 230))
    palette.setColor(QPalette.ColorRole.Button, QColor(42, 45, 50))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 224, 230))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Link, QColor(41, 128, 185))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(53, 116, 240))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

    app.setPalette(palette)

    # QSS Styling for Docks, Toolbars, and Views
    qss = """
    QMainWindow {
        background-color: #1a1c1e;
    }
    
    QMenuBar {
        background-color: #202226;
        color: #dce0e6;
        border-bottom: 1px solid #2d3037;
        font-size: 13px;
    }
    QMenuBar::item {
        background: transparent;
        padding: 6px 12px;
    }
    QMenuBar::item:selected {
        background-color: #2d3037;
        color: #ffffff;
    }
    QMenu {
        background-color: #202226;
        color: #dce0e6;
        border: 1px solid #2d3037;
    }
    QMenu::item {
        padding: 6px 24px 6px 12px;
    }
    QMenu::item:selected {
        background-color: #3574f0;
        color: #ffffff;
    }

    QToolBar {
        background-color: #202226;
        border-bottom: 1px solid #2d3037;
        spacing: 4px;
        padding: 2px;
    }

    QDockWidget {
        color: #dce0e6;
        titlebar-close-icon: url(none);
        titlebar-normal-icon: url(none);
        font-weight: bold;
        font-size: 12px;
    }
    QDockWidget::title {
        background-color: #25282e;
        padding: 8px 12px;
        border-bottom: 1px solid #2d3037;
        text-align: left;
    }

    QTreeWidget, QTableWidget {
        background-color: #18191c;
        border: 1px solid #2d3037;
        color: #dce0e6;
        gridline-color: #2d3037;
    }
    QHeaderView::section {
        background-color: #202226;
        color: #a0a5b0;
        padding: 4px;
        border: 1px solid #2d3037;
        font-weight: bold;
    }

    QStatusBar {
        background-color: #18191c;
        color: #808692;
        border-top: 1px solid #2d3037;
    }
    """
    app.setStyleSheet(qss)