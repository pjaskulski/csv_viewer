from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QDialog, QMessageBox, QDialogButtonBox, QVBoxLayout, QLabel, QLineEdit, \
    QPushButton, QFileDialog, QGroupBox, QGridLayout, QTableView, QAction, QStyle, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
import os


class ApiDatabaseDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(QSize(800, 400))

        config_folder = os.path.join(os.path.expanduser("~"), '.config', 'CSV_Viewer')
        os.makedirs(config_folder, exist_ok=True)
        db_file = "apilinks.sqlite"
        db_path = os.path.join(config_folder, db_file)

        self.db = QSqlDatabase("QSQLITE")
        self.db.setDatabaseName(db_path)
        if self.db.open():
            if os.path.getsize(db_path) == 0:
                query = QSqlQuery(db=self.db)
                query.exec_("CREATE TABLE links(address TEXT)")
                demo = "http://climatedataapi.worldbank.org/climateweb/rest/v1/country/cru/tas/year/POL.csv"
                query.exec_(f"INSERT INTO links VALUES ('{demo}')")
                self.db.commit()
        else:
            QMessageBox.warning(self, "Error", "API links database not open.")

        self.table = QTableView()
        self.model = QSqlTableModel(db=self.db)
        self.model.setTable('links')
        self.model.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.model.select()

        # set headers
        column_titles = {"address": "API Address"}
        for n, t in column_titles.items():
            idx = self.model.fieldIndex(n)
            self.model.setHeaderData(idx, Qt.Horizontal, t)

        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        self.table.setColumnWidth(0, 750)
        self.table.selectRow(0)
        self.table.setFocus()

        self.layout = QVBoxLayout()
        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)

        style_add = self.buttonBox.style()
        icon = style_add.standardIcon(QStyle.SP_DialogYesButton)
        self.button_add = QPushButton(icon, "&Add")
        self.button_add.setStatusTip("Add new api link")
        self.button_add.clicked.connect(self.add_link)

        style_del = self.buttonBox.style()
        icon = style_del.standardIcon(QStyle.SP_DialogNoButton)
        self.button_del = QPushButton(icon, "&Delete")
        self.button_del.setStatusTip("Delete api link")
        self.button_del.clicked.connect(self.del_link)

        self.buttonBox.accepted.connect(self.accept)

        self.layout.addWidget(self.table)
        layout_btn = QHBoxLayout()
        layout_btn.addWidget(self.button_add)
        layout_btn.addWidget(self.button_del)
        layout_btn.addSpacerItem(QSpacerItem(150, 10, QSizePolicy.Expanding))
        layout_btn.addWidget(self.buttonBox)

        self.layout.addLayout(layout_btn)
        self.setLayout(self.layout)

    def closeEvent(self, event) -> None:
        """ Quit dialog """
        self.db.close()

    def add_link(self):
        self.model.insertRows(self.model.rowCount(), 1)
        self.table.setFocus()
        self.table.selectRow(self.model.rowCount() - 1)
        index = self.table.currentIndex()
        self.table.edit(index)

    def del_link(self):
        if self.model.rowCount() > 0:
            index = self.table.currentIndex()
            self.model.removeRow(index.row())
            self.model.submitAll()
            self.table.setRowHidden(index.row(), True)
            if index.row() == 0:
                current = 0
            else:
                current = index.row() - 1
            self.table.selectRow(current)


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
        dlg = ApiDatabaseDialog()
        dlg.setWindowTitle("API database")
        if dlg.exec_():
            index = dlg.table.currentIndex()
            self.address.setText(dlg.model.itemData(index).get(0))
