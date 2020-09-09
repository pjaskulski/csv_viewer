import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QTableView


class SummaryModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role):
        value = self._data.iloc[index.row(), index.column()]
        is_numeric = np.isreal(value) and not isinstance(value, bool)

        if role == Qt.DisplayRole:
            if is_numeric:
                return f"{value:.3f}"  # temporary all numbers as float
            else:
                return str(value)

        if role == Qt.TextAlignmentRole:
            if is_numeric:
                return Qt.AlignVCenter + Qt.AlignRight
            else:
                return Qt.AlignVCenter + Qt.AlignLeft

    def rowCount(self, index):
        # the length of summary (rows)
        return self._data.shape[0]

    def columnCount(self, index):
        # length of summary (columns)
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # header data (first row and first column)
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])


class SummaryDialog(QDialog):
    def __init__(self, summary_data):
        super().__init__()
        self.setMinimumSize(600, 350)
        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.layout = QVBoxLayout()
        self.table = QTableView()
        self.model = SummaryModel(summary_data)
        self.table.setModel(self.model)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
