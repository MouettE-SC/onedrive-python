from PySide6.QtCore import Slot, Qt, QEvent
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QDialog, QGroupBox,
                               QMenu, QMessageBox, QPushButton,
                               QSystemTrayIcon, QVBoxLayout, QTabWidget, QWidget)
import os.path
import logging

from onedrive import VERSION
from onedrive.gui.icons import icons
from onedrive.config import OnedriveConfig
from onedrive.gui.add_account import AddAccount
from onedrive.gui.account_widget import AccountWidget

log = logging.getLogger("gui")


class MainWindow(QDialog):

    def __init__(self, config: OnedriveConfig):
        super().__init__()
        self.config = config

        self.setWindowIcon(icons['cloud'])
        self.setWindowTitle(self.tr("Onedrive"))

        # Main window
        layout = QVBoxLayout()
        self.setLayout(layout)
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Accounts tab
        accounts_tab = QWidget()
        self.accounts_layout = QVBoxLayout()
        tabs.addTab(accounts_tab, self.tr("Accounts"))
        add_account = QPushButton(self.tr("Add account"))
        add_account.clicked.connect(self.add_account)
        self.accounts_layout.addWidget(add_account, alignment=Qt.AlignmentFlag.AlignRight)
        self.accounts_layout.addStretch(1)
        self.accounts_list = QWidget()
        self.accounts_list_layout = QVBoxLayout()
        self.accounts_list.setLayout(self.accounts_list_layout)
        self.accounts_layout.addWidget(self.accounts_list)
        self.populate_accounts()
        accounts_tab.setLayout(self.accounts_layout)

        # Preferences tab
        preferences_tab = QWidget()
        tabs.addTab(preferences_tab, self.tr("Preferences"))

        # Tray menu
        self.preferences_action = QAction()
        self.about_action = QAction()
        self.quit_action = QAction()
        self.setup_actions()

        self.tray_icon = QSystemTrayIcon()
        self.tray_icon_menu = QMenu()
        self.setup_tray()
        if len(config.accounts) == 0:
            self.show()

    def setup_actions(self):
        self.preferences_action = QAction(self.tr("Preferences"), self)
        self.preferences_action.triggered.connect(self.show)
        self.about_action = QAction(self.tr("About"), self)
        self.about_action.triggered.connect(self.about)
        self.quit_action = QAction(self.tr("Quit"), self)
        self.quit_action.triggered.connect(self.quit)

    @Slot()
    def about(self):
        QMessageBox.information(None, self.tr("About"), self.tr("Onedrive client version %s" % (VERSION, )))

    def event(self, event):
        if event.spontaneous() and event.type() == QEvent.Type.WindowStateChange and self.isMinimized():
            self.hide()
            event.ignore()
        return super().event(event)

    def closeEvent(self, event):
        if not event.spontaneous() or not self.isVisible():
            return
        self.hide()
        event.ignore()

    @Slot()
    def quit(self):
        log.info("Quitting Onedrive GUI")
        # TODO quit operations
        qApp.quit()

    def setup_tray(self):
        self.tray_icon_menu = QMenu(self)
        self.tray_icon_menu.addAction(self.preferences_action)
        self.tray_icon_menu.addSeparator()
        self.tray_icon_menu.addAction(self.about_action)
        self.tray_icon_menu.addAction(self.quit_action)
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(icons['off'])
        self.tray_icon.setToolTip(self.tr("Onedrive"))
        self.tray_icon.setContextMenu(self.tray_icon_menu)
        self.tray_icon.activated.connect(self.show)
        self.tray_icon.show()

    def add_account(self):
        a = AddAccount(self, self.config)
        a.accepted.connect(self.append_new_account)
        a.show()

    def append_new_account(self):
        log.info("Appending last create account")
        self.accounts_list_layout.addWidget(AccountWidget(self, self.config.accounts[-1]))

    def populate_accounts(self):
        log.info("Populating accounts list")
        _remove = []
        for i in range(self.accounts_list_layout.count()):
            c = self.accounts_list_layout.itemAt(i).widget()
            if c:
                _remove.append(c)
        for c in _remove:
            c.deleteLater()

        for a in self.config.accounts.values():
           self.accounts_list_layout.addWidget(AccountWidget(self, a))