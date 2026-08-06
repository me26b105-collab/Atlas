"""
Atlas UI Design System
Professional engineering-inspired dark theme.
"""

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


def apply_dark_theme(app: QApplication) -> None:
    """Apply the Atlas design language."""

    app.setStyle("Fusion")

    palette = QPalette()

    palette.setColor(QPalette.ColorRole.Window, QColor("#1B1D22"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#E6EAF0"))

    palette.setColor(QPalette.ColorRole.Base, QColor("#17191D"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#20242B"))

    palette.setColor(QPalette.ColorRole.Text, QColor("#E6EAF0"))

    palette.setColor(QPalette.ColorRole.Button, QColor("#2B3038"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#E6EAF0"))

    palette.setColor(QPalette.ColorRole.Highlight, QColor("#2F7AF8"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))

    palette.setColor(QPalette.ColorRole.Link, QColor("#5EA1FF"))

    app.setPalette(palette)

    app.setStyleSheet("""

    /* =======================================================
                        Main Window
    ======================================================= */

    QMainWindow{
        background:#1B1D22;
    }

    /* =======================================================
                        Menu Bar
    ======================================================= */

    QMenuBar{

        background:#20242B;

        border:none;
        border-bottom:1px solid #343942;

        color:#E6EAF0;

        spacing:6px;

        padding:4px;

        font-size:13px;
    }

    QMenuBar::item{

        padding:7px 14px;

        border-radius:6px;

        background:transparent;

    }

    QMenuBar::item:selected{

        background:#2F7AF8;

        color:white;

    }

    /* =======================================================
                            Menus
    ======================================================= */

    QMenu{

        background:#252A31;

        color:white;

        border:1px solid #3A404A;

        padding:6px;

    }

    QMenu::item{

        padding:8px 30px 8px 12px;

        border-radius:5px;

    }

    QMenu::item:selected{

        background:#2F7AF8;

    }

    /* =======================================================
                        Toolbars
    ======================================================= */

    QToolBar{

        background:#20242B;

        border:none;

        border-bottom:1px solid #343942;

        spacing:6px;

        padding:6px;

    }

    QToolButton{

        background:transparent;

        border-radius:6px;

        padding:6px;

    }

    QToolButton:hover{

        background:#303642;

    }

    QToolButton:pressed{

        background:#2F7AF8;

    }

    /* =======================================================
                        Dock Widgets
    ======================================================= */

    QDockWidget{

        color:white;

        font-size:12px;

        font-weight:bold;

    }

    QDockWidget::title{

        background:#242830;

        border-bottom:1px solid #353B45;

        padding:10px;

        text-align:left;

    }

    /* =======================================================
                            Trees
    ======================================================= */

    QTreeWidget{

        background:#17191D;

        border:none;

        outline:none;

        color:#DCE2EA;

        padding:4px;

    }

    QTreeWidget::item{

        padding:5px;

        border-radius:5px;

    }

    QTreeWidget::item:selected{

        background:#2F7AF8;

        color:white;

    }

    QTreeWidget::item:hover{

        background:#303642;

    }

    /* =======================================================
                            Tables
    ======================================================= */

    QTableWidget{

        background:#17191D;

        border:none;

        gridline-color:#30343B;

        color:#E6EAF0;

    }

    QHeaderView::section{

        background:#20242B;

        color:#9AA3AE;

        border:none;

        border-bottom:1px solid #30343B;

        padding:6px;

    }

    /* =======================================================
                        Status Bar
    ======================================================= */

    QStatusBar{

        background:#20242B;

        border-top:1px solid #353B45;

        color:#A5ADB8;

    }

    /* =======================================================
                        Scrollbars
    ======================================================= */

    QScrollBar:vertical{

        background:#20242B;

        width:12px;

        border:none;

    }

    QScrollBar::handle:vertical{

        background:#4B5563;

        border-radius:5px;

        min-height:24px;

    }

    QScrollBar::handle:vertical:hover{

        background:#6A7483;

    }

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical{

        height:0px;

    }

    QScrollBar:horizontal{

        background:#20242B;

        height:12px;

        border:none;

    }

    QScrollBar::handle:horizontal{

        background:#4B5563;

        border-radius:5px;

        min-width:24px;

    }

    QScrollBar::handle:horizontal:hover{

        background:#6A7483;

    }

    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal{

        width:0px;

    }

    """)