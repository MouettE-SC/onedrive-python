from PySide6.QtWidgets import QDialog, QComboBox, QFormLayout, QPushButton, QVBoxLayout, QWidget, QLayout, QLineEdit, QCheckBox, QGroupBox
from PySide6.QtCore import Qt
from onedrive.gui.icons import icons
from onedrive import endpoints, app_defaults

class AddAccount(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowIcon(icons['cloud'])
        self.setWindowTitle(self.tr("Add account"))
        self.setModal(True)
        layout = QVBoxLayout()
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.setLayout(layout)

        base_w = QWidget()
        layout.addWidget(base_w)
        base_layout = QFormLayout()
        base_w.setLayout(base_layout)
        self.cb = QComboBox()
        for k,v in endpoints.items():
            self.cb.addItem(v['name'], k)
        base_layout.addRow(self.tr('Endpoint:'), self.cb)
        # self.adv_button = QPushButton()
        # self.adv_button.setText(self.tr("Advanced >>"))
        # self.adv_button.setCheckable(True)
        # self.adv_button.toggled.connect(self.switch_advanced)
        # base_layout.addRow(None, self.adv_button)


        self.adv_gb = QGroupBox(self.tr("Advanced"))
        self.adv_gb.setCheckable(True)
        self.adv_gb.setChecked(False)
        layout.addWidget(self.adv_gb)

        self.adv_w = QWidget()
        self.adv_w.setVisible(False)
        self.adv_gb.toggled.connect(lambda _: self.adv_w.setVisible(self.adv_gb.isChecked()))
        adv_w_layout = QVBoxLayout()
        adv_w_layout.setSpacing(0)
        adv_w_layout.setContentsMargins(0, 0, 0, 0)
        self.adv_gb.setLayout(adv_w_layout)
        adv_w_layout.addWidget(self.adv_w)

        adv_layout = QFormLayout()
        self.adv_w.setLayout(adv_layout)
        self.app_id = QLineEdit()
        adv_layout.addRow(self.tr("Application ID:"), self.app_id)
        self.app_name = QLineEdit()
        adv_layout.addRow(self.tr("Application name:"), self.app_name)
        self.app_company_name = QLineEdit()
        adv_layout.addRow(self.tr("Company name:"), self.app_company_name)
        self.app_isv = QCheckBox()
        self.app_isv.setText(self.tr("Independant Software Vendor"))
        adv_layout.addRow(None, self.app_isv)
        self.app_tenant = QLineEdit()
        adv_layout.addRow(self.tr('Tenant:'), self.app_tenant)
        self.app_version = QLineEdit()
        adv_layout.addRow(self.tr("Application version:"), self.app_version)

        self.next_button = QPushButton()
        self.next_button.setText(self.tr("Next >"))
        layout.addWidget(self.next_button, alignment=Qt.AlignmentFlag.AlignRight)


    def switch_advanced(self):
        if self.adv_button.isChecked():
            self.adv_button.setText(self.tr("<< Advanced"))
            self.adv_w.setVisible(True)
        else:
            self.adv_button.setText(self.tr("Advanced >>"))
            self.adv_w.setVisible(False)