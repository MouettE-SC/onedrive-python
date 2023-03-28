from PySide6.QtWidgets import QDialog, QCheckBox, QVBoxLayout
from onedrive.gui.icons import icons

class AddAccount(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowIcon(icons['cloud'])
        self.setWindowTitle(self.tr("Add account"))
        self.setModal(True)
        layout = QVBoxLayout()
        self.setLayout(layout)
        cb = QCheckBox("hello")
        layout.addWidget(cb)
