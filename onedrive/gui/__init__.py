from onedrive.config import OnedriveConfig
from onedrive.gui.main import MainWindow
from PySide6.QtCore import QTranslator, QLocale
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QSystemTrayIcon
from PySide6.QtNetwork import QAbstractSocket
import logging
import socket
import signal
import sys
import os.path

log = logging.getLogger("gui")
app: QApplication


class SignalWatchdog(QAbstractSocket):
    def __init__(self, parent=None):
        """ Propagates system signals from Python to QEventLoop """
        super().__init__(QAbstractSocket.SctpSocket, parent)
        self.writer, self.reader = socket.socketpair()
        self.writer.setblocking(False)
        signal.set_wakeup_fd(self.writer.fileno())  # Python hook
        self.setSocketDescriptor(self.reader.fileno())  # Qt hook
        self.readyRead.connect(lambda: None)  # Dummy function call


def run(config: OnedriveConfig):
    global app
    app = QApplication()
    SignalWatchdog(app)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        log.critical("No system tray available !")
        sys.exit(1)

    translator = QTranslator()
    if translator.load(QLocale(), "", directory=os.path.join(os.path.dirname(__file__), "i18n")):
        app.installTranslator(translator)

    QApplication.setQuitOnLastWindowClosed(False)
    mw = MainWindow(config)
    signal.signal(signal.SIGINT, lambda *a: mw.quit())
    sys.exit(app.exec())
