from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QPlainTextEdit


class InfoDialog(QDialog):
    def __init__(self, info):
        super().__init__()
        self.setMinimumSize(600, 350)
        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.layout = QVBoxLayout()
        self.info_view = QPlainTextEdit()
        self.info_view.setPlainText(info)
        self.info_view.setReadOnly(True)
        self.layout.addWidget(self.info_view)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
