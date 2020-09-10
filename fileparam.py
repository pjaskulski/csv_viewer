from PyQt5.QtWidgets import QDialog, QMessageBox, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QRadioButton, QFileDialog, QGroupBox


class ParameterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(520, 200)
        self.separator = ","
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
        self.layout_file.addWidget(self.filename)
        self.btn_file = QPushButton("...")
        self.btn_file.setMaximumWidth(25)
        self.btn_file.clicked.connect(self.onBtnFileClicked)
        self.layout_file.addWidget(self.btn_file)

        groupbox_sep = QGroupBox("Separator:")
        self.layout.addWidget(groupbox_sep)
        self.layout_sep = QHBoxLayout()
        groupbox_sep.setLayout(self.layout_sep)

        self.radio_comma = QRadioButton("Comma")
        self.radio_comma.setChecked(True)
        self.radio_comma.separator = ","
        self.radio_comma.toggled.connect(self.onClicked)

        self.radio_semicol = QRadioButton("Semicolon")
        self.radio_semicol.setChecked(False)
        self.radio_semicol.separator = ";"
        self.radio_semicol.toggled.connect(self.onClicked)

        self.radio_tab = QRadioButton("Tab")
        self.radio_tab.setChecked(False)
        self.radio_tab.separator = "\t"
        self.radio_tab.toggled.connect(self.onClicked)

        self.layout_sep.addWidget(self.radio_comma)
        self.layout_sep.addWidget(self.radio_semicol)
        self.layout_sep.addWidget(self.radio_tab)

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

    def onBtnFileClicked(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open CSV file...", "", "CSV (*.csv);;All Files (*)")
        if file_name:
            self.filename.setText(file_name)
