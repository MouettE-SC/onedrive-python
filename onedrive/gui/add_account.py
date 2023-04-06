from PySide6.QtWidgets import QDialog, QComboBox, QFormLayout, QPushButton, QVBoxLayout,\
    QWidget, QLayout, QLineEdit, QCheckBox, QGroupBox, QSpacerItem, QStackedWidget, QLabel
from PySide6.QtCore import Qt

from onedrive import app_defaults
from onedrive.gui.icons import icons
from onedrive.gui.wait_spinner import QtWaitingSpinner
from onedrive import endpoints
from uuid import UUID
from onedrive.account import Account
from onedrive.api import OneDriveAPI
from onedrive.config import OnedriveConfig

class AddAccount(QDialog):

    def __init__(self, parent, config: OnedriveConfig):
        super().__init__(parent)
        self.config = config
        self.setWindowIcon(icons['cloud'])
        self.setWindowTitle(self.tr("Add account"))
        self.setModal(True)

        self.account = Account()
        self.api = OneDriveAPI(config, self.account, self)

        ## Main window stack widget
        self.stacked_w = QStackedWidget()
        layout = QVBoxLayout()
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        layout.addWidget(self.stacked_w)
        self.setLayout(layout)

        ## Step 0 widget (main account form)
        self.step0_w = QWidget()
        self.stacked_w.addWidget(self.step0_w)
        self.step0_layout = QVBoxLayout()
        self.step0_layout.setSpacing(0)
        self.step0_layout.setContentsMargins(0, 0, 0, 0)
        self.step0_w.setLayout(self.step0_layout)

        self.initial_endpoint = config.get('app-defaults', 'endpoint', fallback=app_defaults['endpoint'])
        self.initial_app_id = config.get('app-defaults', 'application-id', fallback=app_defaults['id'])
        self.initial_app_name = config.get('app-defaults', 'application-name', fallback=app_defaults['name'])
        self.initial_app_company_name = config.get('app-defaults', 'company-name', fallback=app_defaults['company_name'])
        self.initial_app_isv = config.getboolean('app-defaults', 'isv', fallback=app_defaults['isv'])
        self.initial_app_tenant = config.get('app-defaults', 'tenant', fallback=app_defaults['tenant'])
        self.initial_app_version = config.get('app-defaults', 'version', fallback=app_defaults['version'])

        # base account form (endpoint)
        base_w = QWidget()
        self.step0_layout.addWidget(base_w)
        base_layout = QFormLayout()
        base_w.setLayout(base_layout)
        self.endpoints_cb = QComboBox()
        self.endpoints_map = {}
        i = 0
        for k,v in endpoints.items():
            self.endpoints_cb.addItem(v['name'])
            self.endpoints_map[i] = k
            if k == self.initial_endpoint:
                self.endpoints_cb.setCurrentIndex(i)
            i += 1
        base_layout.addRow(self.tr('Endpoint:'), self.endpoints_cb)

        # advanced account form (application), hidden by default
        self.adv_gb = QGroupBox(self.tr("Advanced"))
        self.adv_gb.setCheckable(True)
        self.adv_gb.setChecked(config.has_section('app-default'))
        self.step0_layout.addWidget(self.adv_gb)

        self.adv_w = QWidget()
        self.adv_w.setVisible(False)
        self.adv_gb.toggled.connect(self.switch_advanced)
        adv_w_layout = QVBoxLayout()
        adv_w_layout.setSpacing(0)
        adv_w_layout.setContentsMargins(0, 0, 0, 0)
        self.adv_gb.setLayout(adv_w_layout)
        adv_w_layout.addWidget(self.adv_w)

        adv_layout = QFormLayout()
        self.adv_w.setLayout(adv_layout)
        self.app_id = QLineEdit()
        self.app_id.setText(self.initial_app_id)
        self.app_id.setMinimumWidth(260)
        self.app_id.editingFinished.connect(self.validate_step0)
        adv_layout.addRow(self.tr("Application ID:"), self.app_id)
        self.app_name = QLineEdit()
        self.app_name.setText(self.initial_app_name)
        self.app_name.editingFinished.connect(self.validate_step0)
        adv_layout.addRow(self.tr("Application name:"), self.app_name)
        self.app_company_name = QLineEdit()
        self.app_company_name.setText(self.initial_app_company_name)
        self.app_company_name.editingFinished.connect(self.validate_step0)
        adv_layout.addRow(self.tr("Company name:"), self.app_company_name)
        self.app_isv = QCheckBox()
        self.app_isv.setChecked(self.initial_app_isv)
        self.app_isv.setText(self.tr("Independant Software Vendor"))
        adv_layout.addRow(None, self.app_isv)
        self.app_tenant = QLineEdit()
        self.app_tenant.setText(self.initial_app_tenant)
        self.app_tenant.editingFinished.connect(self.validate_step0)
        adv_layout.addRow(self.tr('Tenant:'), self.app_tenant)
        self.app_version = QLineEdit()
        self.app_version.setText(self.initial_app_version)
        self.app_version.editingFinished.connect(self.validate_step0)
        adv_layout.addRow(self.tr("Application version:"), self.app_version)

        self.step0_layout.addSpacerItem(QSpacerItem(0, 10))

        self.next_button = QPushButton()
        self.next_button.setText(self.tr("Next >"))
        self.next_button.clicked.connect(self.next)
        self.step0_layout.addWidget(self.next_button, alignment=Qt.AlignmentFlag.AlignRight)

        ## Step 1 widget (login attempt)
        step1_w = QWidget()
        self.stacked_w.addWidget(step1_w)
        step1_layout = QVBoxLayout()
        step1_layout.setSpacing(0)
        step1_layout.setContentsMargins(0, 0, 0, 0)
        step1_layout.setSpacing(20)
        step1_w.setLayout(step1_layout)
        step1_help = QLabel()
        step1_help.setText(self.tr("Please login and allow application in your browser"))
        step1_layout.addWidget(step1_help)
        self.step1_ws = QtWaitingSpinner(None)
        self.step1_ws.setRoundness(70)
        self.step1_ws.setMinimumTrailOpacity(10)
        self.step1_ws.setTrailFadePercentage(75)
        self.step1_ws.setNumberOfLines(20)
        self.step1_ws.setLineLength(50)
        self.step1_ws.setLineWidth(7)
        self.step1_ws.setInnerRadius(30)
        self.step1_ws.setRevolutionsPerSecond(0.6)
        step1_layout.addWidget(self.step1_ws, alignment=Qt.AlignmentFlag.AlignCenter)
        step1_cancel = QPushButton()
        step1_cancel.setText(self.tr("Cancel"))
        step1_cancel.clicked.connect(self.cancel)
        step1_layout.addWidget(step1_cancel, alignment=Qt.AlignmentFlag.AlignRight)

    def switch_advanced(self):
        if self.adv_gb.isChecked():
            self.app_id.setFocus()
            self.adv_w.setVisible(True)
            self.validate_step0()
        else:
            self.adv_w.setVisible(False)
            self.next_button.setEnabled(True)

    @staticmethod
    def validate_not_empty(ql):
        if len(ql.text()) == 0:
            ql.setStyleSheet("color: #9C0006; background-color: #ffc7ce")
            return False
        ql.setStyleSheet("")
        return True

    def validate_step0(self):
        self.next_button.setEnabled(self.check_step0())
    def check_step0(self):
        if not self.adv_gb.isChecked():
            return True
        try:
            if len(self.app_id.text()) == 0 or UUID(self.app_id.text()).version != 4:
                self.app_id.setStyleSheet("color: #9C0006; background-color: #ffc7ce")
                return False
        except ValueError:
            self.app_id.setStyleSheet("color: #9C0006; background-color: #ffc7ce")
            return False
        self.app_id.setStyleSheet("")
        if not self.validate_not_empty(self.app_name):
            return False
        if not self.validate_not_empty(self.app_company_name):
            return False
        if not self.validate_not_empty(self.app_tenant):
            return False
        if not self.validate_not_empty(self.app_version):
            return False
        return True

    def next(self):
        if not self.check_step0():
            self.next_button.setEnabled(False)
        else:
            self.step1_ws.start()
            self.stacked_w.setCurrentIndex(1)
            self.account = Account({
                'application_id': self.app_id.text(),
                'application_name': self.app_name.text(),
                'application_version': self.app_version.text(),
                'company_name': self.app_company_name.text(),
                'isc': self.app_isv.isChecked(),
                'tenant': self.app_tenant.text(),
                'endpoint': self.endpoints_map[self.endpoints_cb.currentIndex()]
            })
            self.api = OneDriveAPI(self.config, self.account, self)
            self.api.start_auth(self.auth_ended)

    def auth_ended(self, valid: bool):
        if not valid:
            self.reject()
        else:
            self.accept()

    def cancel(self):
        self.api.cancel_auth()
        self.reject()