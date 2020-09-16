from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QMessageBox, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, \
    QPushButton, QRadioButton, QFileDialog, QGroupBox, QSpacerItem, QGridLayout


class ApiDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(520, 200)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.validate)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()

        # group box
        groupbox = QGroupBox("API address and CSV file path:")
        self.layout.addWidget(groupbox)
        self.layout_grid = QGridLayout()
        groupbox.setLayout(self.layout_grid)

        # API address
        label_addres = QLabel("Address:")
        self.layout_grid.addWidget(label_addres, 0, 0)
        self.address = QLineEdit()
        self.address.setText('')
        self.layout_grid.addWidget(self.address, 0, 1)
        self.btn_api = QPushButton("...")
        self.btn_api.setMaximumWidth(25)
        self.btn_api.clicked.connect(self.onBtnApiClicked)
        self.layout_grid.addWidget(self.btn_api, 0, 2)

        # file name to save
        label_fname = QLabel("Path:")
        self.layout_grid.addWidget(label_fname, 1, 0)
        self.filename = QLineEdit()
        self.filename.setText('')
        self.layout_grid.addWidget(self.filename, 1, 1)
        self.btn_file = QPushButton("...")
        self.btn_file.setMaximumWidth(25)
        self.btn_file.clicked.connect(self.onBtnFileClicked)
        self.layout_grid.addWidget(self.btn_file, 1, 2)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def validate(self):
        if self.address.text() == '':
            QMessageBox.about(self, 'Error', 'API address is mandatory.')
            self.address.setFocus()
        elif self.filename.text() == '':
            QMessageBox.about(self, 'Error', 'Path to save CSV file is mandatory.')
            self.filename.setFocus()
        else:
            self.accept()

    def onBtnFileClicked(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save CSV file...", "", "CSV (*.csv);;All Files (*)")
        if file_name:
            self.filename.setText(file_name)

    def onBtnApiClicked(self):
        pass
