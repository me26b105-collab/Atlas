"""Atlas Toolbar Component."""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QToolBar


class AtlasToolBar(QToolBar):
    """Main application toolbar designed to accommodate quick actions/tools."""

    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)
        self.setObjectName("MainToolBar")
        self.setMovable(False)
        self.setIconSize(QSize(20, 20))
        
        # Initialized empty as requested for extension