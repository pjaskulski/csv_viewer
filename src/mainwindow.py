import io
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QToolBar, QAction, QStatusBar, QStyle, QMessageBox, QLabel, QFileDialog
from PyQt5.QtCore import Qt, QSize, QSettings, QFileInfo
from summary import SummaryDialog
from fileparam import ParameterDialog
from about import AboutDialog
from info import InfoDialog


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
    MaxRecentFiles = 5

    def __init__(self, app_title):
        super().__init__()
        self.app_title = app_title
        self.setMinimumSize(600, 300)
        self.df = None
        self.recentFileActs = []

        # toolbar
        self.toolbar = QToolBar("MainToolbar")
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(self.toolbar)

        # open action
        style = self.toolbar.style()
        icon = style.standardIcon(QStyle.SP_FileDialogStart)
        self.button_open = QAction(icon, "Open", self)
        self.button_open.setShortcut('Ctrl+O')
        self.button_open.setStatusTip("Open CSV file...")
        self.button_open.triggered.connect(self.onToolbarOpenButtonClick)
        self.toolbar.addAction(self.button_open)

        # summary action
        style_summary = self.toolbar.style()
        icon = style_summary.standardIcon(QStyle.SP_FileDialogListView)
        self.button_summary = QAction(icon, "Summary", self)
        self.button_summary.setShortcut('Ctrl+S')
        self.button_summary.setStatusTip("Show summary for the current file")
        self.button_summary.triggered.connect(self.onToolbarSummaryButtonClick)
        self.toolbar.addAction(self.button_summary)
        self.button_summary.setEnabled(False)

        # info action
        style_info = self.toolbar.style()
        icon = style_info.standardIcon(QStyle.SP_FileIcon)
        self.button_info = QAction(icon, "Info", self)
        self.button_info.setShortcut('Ctrl+I')
        self.button_info.setStatusTip("Show summary for the current file")
        self.button_info.triggered.connect(self.onToolbarInfoButtonClick)
        self.toolbar.addAction(self.button_info)
        self.button_info.setEnabled(False)

        # resize action
        style_resize = self.toolbar.style()
        icon = style_resize.standardIcon(QStyle.SP_BrowserReload)
        self.button_resize = QAction(icon, "Resize columns", self)
        self.button_resize.setShortcut('Ctrl+R')
        self.button_resize.setStatusTip("Resize columns width to content")
        self.button_resize.triggered.connect(self.onResizeColumns)
        self.toolbar.addAction(self.button_resize)
        self.button_resize.setEnabled(False)

        # export to xlsx action
        style_xlsx = self.toolbar.style()
        icon = style_xlsx.standardIcon(QStyle.SP_FileLinkIcon)
        self.button_xlsx = QAction(icon, "Xlsx", self)
        self.button_xlsx.setStatusTip("Export data to xlsx file")
        self.button_xlsx.triggered.connect(self.onExportXlsx)
        self.toolbar.addAction(self.button_xlsx)
        self.button_xlsx.setEnabled(False)

        # export to sqlite action
        style_sqlite = self.toolbar.style()
        icon = style_sqlite.standardIcon(QStyle.SP_FileLinkIcon)
        self.button_sqlite = QAction(icon, "SQLite", self)
        self.button_sqlite.setStatusTip("Export data to SQLite database")
        self.button_sqlite.triggered.connect(self.onExportSQLite)
        self.toolbar.addAction(self.button_sqlite)
        self.button_sqlite.setEnabled(False)

        # export to html action
        style_html = self.toolbar.style()
        icon = style_html.standardIcon(QStyle.SP_FileLinkIcon)
        self.button_html = QAction(icon, "HTML", self)
        self.button_html.setStatusTip("Export data to HTML file")
        self.button_html.triggered.connect(self.onExportHTML)
        self.toolbar.addAction(self.button_html)
        self.button_html.setEnabled(False)

        # close action
        style_close = self.toolbar.style()
        icon = style_close.standardIcon(QStyle.SP_DialogCloseButton)
        self.button_close = QAction(icon, "Close", self)
        self.button_close.setShortcut('Ctrl+X')
        self.button_close.setStatusTip("Close CSV file...")
        self.button_close.triggered.connect(self.onToolbarCloseButtonClick)
        self.toolbar.addAction(self.button_close)
        self.button_close.setEnabled(False)

        # quit action
        self.button_quit = QAction("Quit", self)
        self.button_quit.setShortcut('Ctrl+Q')
        self.button_quit.setStatusTip("Quit application")
        self.button_quit.triggered.connect(self.close)

        # about action
        style_about = self.toolbar.style()
        icon = style_about.standardIcon(QStyle.SP_FileDialogInfoView)
        self.button_about = QAction(icon, "About", self)
        self.button_about.setStatusTip("About application")
        self.button_about.triggered.connect(self.about)
        self.toolbar.addAction(self.button_about)
        self.button_about.setEnabled(True)

        # recent menu action
        for i in range(MainWindow.MaxRecentFiles):
            self.recentFileActs.append(
                QAction(self, visible=False, triggered=self.openRecentFile)
            )

        # menu bar
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(self.button_open)
        file_menu.addAction(self.button_close)
        self.separatorAct = file_menu.addSeparator()

        for i in range(MainWindow.MaxRecentFiles):
            file_menu.addAction(self.recentFileActs[i])
        file_menu.addSeparator()

        file_menu.addAction(self.button_quit)

        view_menu = menu.addMenu("Vie&w")
        view_menu.addAction(self.button_summary)
        view_menu.addAction(self.button_info)
        view_menu.addSeparator()
        view_menu.addAction(self.button_resize)

        export_menu = menu.addMenu("&Export")
        export_menu.addAction(self.button_xlsx)
        export_menu.addAction(self.button_sqlite)
        export_menu.addAction(self.button_html)

        help_menu = menu.addMenu("&Help")
        help_menu.addAction(self.button_about)

        self.updateRecentFileActions()

        # status bar
        self.my_status = QStatusBar(self)
        self.labelStatus = QLabel("Rows: 0 Cols: 0")
        self.my_status.addPermanentWidget(self.labelStatus)
        self.setStatusBar(self.my_status)

        # set TableView
        self.table = QtWidgets.QTableView()
        self.table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QTableView.SingleSelection)

        self.setCentralWidget(self.table)
        self.setWindowTitle(self.app_title)
        self.setMinimumSize(400, 250)
        self.setGeometry(200, 100, 1000, 600)

    def onToolbarOpenButtonClick(self):
        """ Show open dialog """

        dlg = ParameterDialog()
        dlg.setWindowTitle("Open")
        if dlg.exec_():
            file_name = dlg.filename.text()
            separator = dlg.separator
            decimal = dlg.decimal
        else:
            file_name = None

        if file_name:
            self.saveRecent(file_name)
            self.open_csv_file(file_name, separator, decimal)

    def onOpenRecentFile(self, file_name, sep=',', decimal='.'):
        """ Open file from recent list, show open dialog """

        dlg = ParameterDialog(file_name, sep, decimal)
        dlg.setWindowTitle("Open")
        if dlg.exec_():
            file_name = dlg.filename.text()
            separator = dlg.separator
            decimal = dlg.decimal
        else:
            file_name = None

        if file_name:
            self.saveRecent(file_name)
            self.open_csv_file(file_name, separator, decimal)

    def open_csv_file(self, file_name, sep=',', decimal="."):
        """ Open csv file, load to tableview, set statusbar, enable close icon"""
        try:
            data = pd.read_csv(file_name, sep=sep, decimal=decimal)
            self.df = data
            self.model = TableModel(data)
            self.labelStatus.setText(f"Rows: {data.shape[0]} Cols: {data.shape[1]}")
            self.table.setModel(self.model)
            if data.shape[0] > 0:
                self.table.selectRow(0)

            self.button_close.setEnabled(True)
            self.button_summary.setEnabled(True)
            self.button_info.setEnabled(True)
            self.button_resize.setEnabled(True)
            self.button_xlsx.setEnabled(True)
            self.button_sqlite.setEnabled(True)
            self.button_html.setEnabled(True)
            self.setWindowTitle(self.app_title + ": " + file_name)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f"Error loading the file:\n {file_name}")

    def onResizeColumns(self):
        """Resize columns action, run from menu View->Resize columns"""
        self.table.resizeColumnsToContents()

    def onToolbarCloseButtonClick(self):
        """Clear tableview, set statusbar and disable toolbar close, summary and info icons"""
        self.table.setModel(None)
        self.df = None
        self.button_close.setEnabled(False)
        self.button_summary.setEnabled(False)
        self.button_info.setEnabled(False)
        self.button_resize.setEnabled(False)
        self.button_xlsx.setEnabled(False)
        self.button_sqlite.setEnabled(False)
        self.button_html.setEnabled(False)
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

    def onExportXlsx(self):
        """ Export data to xlsx file """
        file_name, _ = QFileDialog.getSaveFileName(self, 'Export to xlsx', '', ".xlsx(*.xlsx)")
        if file_name:
            self.df.to_excel(file_name, engine='xlsxwriter')

    def onExportSQLite(self):
        """ Export data to sqlite database """
        file_name, _ = QFileDialog.getSaveFileName(self, 'Export to sqlite db', '', ".sqlite(*.sqlite)")
        if file_name:
            engine = create_engine(f'sqlite:///{file_name}', echo=False)
            self.df.to_sql('csv_data', con=engine)

    def onExportHTML(self):
        """ Export data to HTML file """
        file_name, _ = QFileDialog.getSaveFileName(self, 'Export to HTML file', '', ".html(*.html)")
        if file_name:
            self.df.to_html(file_name)

    def closeEvent(self, event):
        """ Quit application, ask user before """
        result = QMessageBox.question(
            self, self.app_title,
            "Are you sure you want to quit?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if result == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def about(self):
        """ Show About dialog (info about application)"""
        dlg = AboutDialog()
        dlg.exec_()

    def openRecentFile(self):
        """ Open file from recent list action """
        action = self.sender()
        if action:
            self.onOpenRecentFile(action.data())

    def saveRecent(self, file_name):
        """ Save information about currently opened file, update recent list"""
        settings = QSettings('CSV_Viewer', 'CSV_Viewer')
        files = settings.value('recentFileList', [])

        try:
            files.remove(file_name)
        except ValueError:
            pass

        files.insert(0, file_name)
        del files[MainWindow.MaxRecentFiles:]

        settings.setValue('recentFileList', files)

        for widget in QtWidgets.QApplication.topLevelWidgets():
            if isinstance(widget, MainWindow):
                widget.updateRecentFileActions()

    def updateRecentFileActions(self):
        """ Update recent file list """
        settings = QSettings('CSV_Viewer', 'CSV_Viewer')
        files = settings.value('recentFileList', [])

        numRecentFiles = min(len(files), MainWindow.MaxRecentFiles)

        for i in range(numRecentFiles):
            text = "&%d %s" % (i + 1, self.strippedName(files[i]))
            self.recentFileActs[i].setText(text)
            self.recentFileActs[i].setData(files[i])
            self.recentFileActs[i].setVisible(True)

        for j in range(numRecentFiles, MainWindow.MaxRecentFiles):
            self.recentFileActs[j].setVisible(False)

        self.separatorAct.setVisible((numRecentFiles > 0))

    def strippedName(self, fullFileName):
        """ Return only file name, without path"""
        return QFileInfo(fullFileName).fileName()

