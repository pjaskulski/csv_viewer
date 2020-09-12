from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(480, 200)
        self.setWindowTitle("About")
        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()

        app_name = QLabel("CSV Viewer")
        font = app_name.font()
        font.setPointSize(30)
        app_name.setFont(font)
        app_name.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        app_name.setStyleSheet("padding: 15px")

        app_ver = QLabel("Version: 0.1")
        font = app_ver.font()
        font.setPointSize(14)
        app_ver.setFont(font)
        app_ver.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        app_author = QLabel("Author: Piotr Jaskulski")
        font = app_author.font()
        font.setPointSize(14)
        app_author.setFont(font)
        app_author.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        app_license = QLabel("License: GPL-3")
        font = app_license.font()
        font.setPointSize(14)
        app_license.setFont(font)
        app_license.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.layout.addWidget(app_name)
        self.layout.addWidget(app_ver)
        self.layout.addWidget(app_author)
        self.layout.addWidget(app_license)

        self.setLayout(self.layout)