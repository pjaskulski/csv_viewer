from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QMessageBox, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, \
    QPushButton, QRadioButton, QFileDialog, QGroupBox, QSpacerItem


class ApiDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(520, 200)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.validate)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()

        # api address to get
        groupbox_api = QGroupBox("API:")
        self.layout.addWidget(groupbox_api)
        self.layout_api = QHBoxLayout()
        groupbox_api.setLayout(self.layout_api)

        self.layout_api.addWidget(QLabel("Address:"))
        self.address = QLineEdit()
        self.address.setText('')
        self.layout_api.addWidget(self.address)

        # file name to save
        groupbox_file = QGroupBox("Path to CSV file:")
        self.layout.addWidget(groupbox_file)
        self.layout_file = QHBoxLayout()
        groupbox_file.setLayout(self.layout_file)

        self.layout_file.addWidget(QLabel("Filename:"))
        self.filename = QLineEdit()
        self.filename.setText('')
        self.layout_file.addWidget(self.filename)
        self.btn_file = QPushButton("...")
        self.btn_file.setMaximumWidth(25)
        self.btn_file.clicked.connect(self.onBtnFileClicked)
        self.layout_file.addWidget(self.btn_file)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def validate(self):
        if self.filename.text() == '':
            QMessageBox.about(self, 'Error', 'Path to save CSV file is mandatory.')
            self.filename.setFocus()
        elif self.address.text() == '':
            QMessageBox.about(self, 'Error', 'API address is mandatory.')
            self.address.setFocus()
        else:
            self.accept()

    def onBtnFileClicked(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save CSV file...", "", "CSV (*.csv);;All Files (*)")
        if file_name:
            self.filename.setText(file_name)
