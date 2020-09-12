from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QMessageBox, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, \
    QPushButton, QRadioButton, QFileDialog, QGroupBox, QSpacerItem


class ParameterDialog(QDialog):
    def __init__(self, file_name='', sep=',', decimal='.'):
        super().__init__()
        self.setMinimumSize(520, 200)
        self.separator = sep
        self.decimal = decimal
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.validate)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()

        groupbox_file = QGroupBox("Path to CSV file:")
        self.layout.addWidget(groupbox_file)
        self.layout_file = QHBoxLayout()
        groupbox_file.setLayout(self.layout_file)

        self.layout_file.addWidget(QLabel("File:"))
        self.filename = QLineEdit()
        self.filename.setText(file_name)
        self.layout_file.addWidget(self.filename)
        self.btn_file = QPushButton("...")
        self.btn_file.setMaximumWidth(25)
        self.btn_file.clicked.connect(self.onBtnFileClicked)
        self.layout_file.addWidget(self.btn_file)

        # separator and decimal group
        self.layout_sepdec = QHBoxLayout()

        # separator (delimiter)
        groupbox_sep = QGroupBox("Separator:")
        self.layout_sepdec.addWidget(groupbox_sep)
        self.layout_sep = QVBoxLayout()
        self.layout_sep.setAlignment(QtCore.Qt.AlignCenter)
        groupbox_sep.setLayout(self.layout_sep)

        self.radio_comma = QRadioButton("Comma")
        self.radio_comma.setChecked(sep == ',')
        self.radio_comma.separator = ","
        self.radio_comma.toggled.connect(self.onClicked)

        self.radio_semicol = QRadioButton("Semicolon")
        self.radio_semicol.setChecked(sep == ';')
        self.radio_semicol.separator = ";"
        self.radio_semicol.toggled.connect(self.onClicked)

        self.radio_tab = QRadioButton("Tab")
        self.radio_tab.setChecked(sep == '\t')
        self.radio_tab.separator = "\t"
        self.radio_tab.toggled.connect(self.onClicked)

        self.layout_sep.addWidget(self.radio_comma)
        self.layout_sep.addWidget(self.radio_semicol)
        self.layout_sep.addWidget(self.radio_tab)

        # decimal point
        groupbox_dp = QGroupBox("Decimal point:")
        self.layout_sepdec.addWidget(groupbox_dp)
        self.layout_dp = QVBoxLayout()
        self.layout_dp.setAlignment(QtCore.Qt.AlignCenter)

        groupbox_dp.setLayout(self.layout_dp)

        self.radio_dp_dot = QRadioButton("Dot")
        self.radio_dp_dot.setChecked(decimal == '.')
        self.radio_dp_dot.decimal = "."
        self.radio_dp_dot.toggled.connect(self.onClickedDecimal)

        self.radio_dp_comma = QRadioButton("Comma")
        self.radio_dp_comma.setChecked(decimal == ',')
        self.radio_dp_comma.decimal = ","
        self.radio_dp_comma.toggled.connect(self.onClickedDecimal)

        self.layout_dp.addWidget(self.radio_dp_dot)
        self.layout_dp.addWidget(self.radio_dp_comma)
        #

        self.layout.addLayout(self.layout_sepdec)
        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

    def validate(self):
        if self.filename.text() == '':
            QMessageBox.about(self, 'Error', 'Path to CSV file is mandatory.')
        else:
            self.accept()

    def onClicked(self):
        radio = self.sender()
        if radio.isChecked():
            self.separator = radio.separator

    def onClickedDecimal(self):
        radio = self.sender()
        if radio.isChecked():
            self.decimal = radio.decimal

    def onBtnFileClicked(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open CSV file...", "", "CSV (*.csv);;All Files (*)")
        if file_name:
            self.filename.setText(file_name)
