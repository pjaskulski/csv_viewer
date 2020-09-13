from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QTableView


class InfoModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(InfoModel, self).__init__()
        self._data = data
        self.columns = [' Column name ', ' Column type ', ' Non-null count ']

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data[index.row()][index.column()]
            if isinstance(value, str):
                return value
            else:
                return str(value)

        if role == Qt.TextAlignmentRole:
            value = index.column()
            if value == 2:
                return Qt.AlignVCenter + Qt.AlignRight
            else:
                return Qt.AlignVCenter + Qt.AlignLeft

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.columns[section]

            if orientation == Qt.Vertical:
                return str(section + 1)


class InfoDialog(QDialog):
    def __init__(self, df):
        super().__init__()
        self.setMinimumSize(600, 350)
        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.layout = QVBoxLayout()

        # info about columns
        c_names = df.columns.values.tolist()
        c_tab = []
        for item in c_names:
            c_tab.append([item, df.dtypes[item], df[item].notnull().sum()])

        self.table = QTableView()
        self.model = InfoModel(c_tab)
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()

        self.layout.addWidget(self.table)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
