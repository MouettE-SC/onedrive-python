from PySide6.QtWidgets import QWidget, QGroupBox, QVBoxLayout
from PySide6.QtCore import QObject

from onedrive.account import Account


class AccountWidget(QGroupBox):

    def __init__(self, parent, account:Account):
        super().__init__(parent)
        self.setTitle(account.description)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
