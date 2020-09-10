import sys
import io
import numpy as np
import pandas as pd
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QToolBar, QAction, QStatusBar, QStyle, QMessageBox, QLabel
from PyQt5.QtCore import Qt, QSize
from summary import SummaryDialog
from fileparam import ParameterDialog
from about import AboutDialog
from info import InfoDialog


app_title = "CSV Viewer"


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]

            if np.isreal(value) and not isinstance(value, bool):
                return f"{value:.2f}"  # temporary all numbers as float
            else:
                return str(value)

        if role == Qt.TextAlignmentRole:
            return Qt.AlignVCenter + Qt.AlignRight

        if role == Qt.ForegroundRole:
            if pd.isna(self._data.iloc[index.row(), index.column()]):
                return QtGui.QColor("red")

    def rowCount(self, index):
        # the length of csv file (rows)
        return self._data.shape[0]

    def columnCount(self, index):
        # length of csv file (columns)
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # header data (first row and first column)
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 300)
        self.df = None

        # toolbar
        self.toolbar = QToolBar("MainToolbar")
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(self.toolbar)

        # open action
        style = self.toolbar.style()
        icon = style.standardIcon(QStyle.SP_FileDialogStart)
        self.button_open = QAction(icon, "Open", self)
        self.button_open.setStatusTip("Open CSV file...")
        self.button_open.triggered.connect(self.onToolbarOpenButtonClick)
        self.toolbar.addAction(self.button_open)

        # summary action
        style_close = self.toolbar.style()
        icon = style_close.standardIcon(QStyle.SP_FileDialogListView)
        self.button_summary = QAction(icon, "Summary", self)
        self.button_summary.setStatusTip("Show summary for the current file")
        self.button_summary.triggered.connect(self.onToolbarSummaryButtonClick)
        self.toolbar.addAction(self.button_summary)
        self.button_summary.setEnabled(False)

        # info action
        style_info = self.toolbar.style()
        icon = style_info.standardIcon(QStyle.SP_FileDialogInfoView)
        self.button_info = QAction(icon, "Info", self)
        self.button_info.setStatusTip("Show summary for the current file")
        self.button_info.triggered.connect(self.onToolbarInfoButtonClick)
        self.toolbar.addAction(self.button_info)
        self.button_info.setEnabled(False)

        # close action
        style_close = self.toolbar.style()
        icon = style_close.standardIcon(QStyle.SP_DialogCloseButton)
        self.button_close = QAction(icon, "Close", self)
        self.button_close.setStatusTip("Close CSV file...")
        self.button_close.triggered.connect(self.onToolbarCloseButtonClick)
        self.toolbar.addAction(self.button_close)
        self.button_close.setEnabled(False)

        # quit action
        self.button_quit = QAction("Quit", self)
        self.button_quit.setStatusTip("Quit application")
        self.button_quit.triggered.connect(self.close)

        # about action
        self.button_about = QAction("About", self)
        self.button_about.setStatusTip("About application")
        self.button_about.triggered.connect(self.about)

        # menu bar
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(self.button_open)
        file_menu.addAction(self.button_summary)
        file_menu.addAction(self.button_info)
        file_menu.addAction(self.button_close)
        file_menu.addSeparator()
        file_menu.addAction(self.button_quit)
        help_menu = menu.addMenu("&Help")
        help_menu.addAction(self.button_about)

        # status bar
        self.my_status = QStatusBar(self)
        self.labelStatus = QLabel("Rows: 0 Cols: 0")
        self.my_status.addPermanentWidget(self.labelStatus)
        self.setStatusBar(self.my_status)

        self.table = QtWidgets.QTableView()
        self.table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QTableView.SingleSelection)

        self.setCentralWidget(self.table)
        self.setWindowTitle(app_title)
        self.setMinimumSize(400, 250)
        self.setGeometry(200, 100, 1000, 600)

    def onToolbarOpenButtonClick(self):
        """ Open csv file, load to tableview, set statusbar, enable close icon"""

        dlg = ParameterDialog()
        dlg.setWindowTitle("Open")
        if dlg.exec_():
            file_name = dlg.filename.text()
            separator = dlg.separator
        else:
            file_name = None

        if file_name:
            try:
                data = pd.read_csv(file_name, sep=separator, decimal=".")
                print(separator)
                self.df = data
                self.model = TableModel(data)
                self.labelStatus.setText(f"Rows: {data.shape[0]} Cols: {data.shape[1]}")
                self.table.setModel(self.model)
                if data.shape[0] > 0:
                    self.table.selectRow(0)
                self.button_close.setEnabled(True)
                self.button_summary.setEnabled(True)
                self.button_info.setEnabled(True)
                self.setWindowTitle(app_title + ": " + file_name)
            except Exception:
                pass

    def onToolbarCloseButtonClick(self):
        """Clear tableview, set statusbar and disable toolbar close icon"""
        self.table.setModel(None)
        self.df = None
        self.button_close.setEnabled(False)
        self.button_summary.setEnabled(False)
        self.button_info.setEnabled(False)
        self.labelStatus.setText("Rows: 0 Cols: 0")

    def onToolbarSummaryButtonClick(self):
        """Show Summary dialog"""
        dlg = SummaryDialog(self.df.describe())
        dlg.setWindowTitle("Summary")
        dlg.exec_()

    def onToolbarInfoButtonClick(self):
        """Show Info dialog"""
        buf = io.StringIO()
        self.df.info(buf=buf)
        tmp = buf.getvalue()

        dlg = InfoDialog(tmp)
        dlg.setWindowTitle("Info")
        dlg.exec_()

    def closeEvent(self, event):
        """ Quit application, ask user before """
        result = QMessageBox.question(
            self, app_title,
            "Are you sure you want to quit?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if result == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
