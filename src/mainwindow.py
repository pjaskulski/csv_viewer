import io
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QToolBar, QAction, QStatusBar, QStyle, QMessageBox, QLabel, QFileDialog, QInputDialog,\
    QProgressBar
from PyQt5.QtCore import Qt, QSize, QSettings, QFileInfo, QRunnable, QThreadPool, pyqtSlot, QObject, pyqtSignal
from summary import SummaryDialog
from fileparam import ParameterDialog
from apiparam import ApiDialog
from about import AboutDialog
from info import InfoDialog
import dataload
import time
import sys



if "pytest" in sys.modules:
    app_test = True
else:
    app_test = False


class WorkerSignals(QObject):
    progress = pyqtSignal(int)
    status = pyqtSignal(bool)


class MarkdownWorker(QRunnable):
    """ export worker (thread) """

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        """ run thread worker """
        file_name = self.args[0]
        df = self.args[1]
        self.signals.status.emit(True)
        with open(file_name, 'w') as f:
            size = df.shape[0]
            counter = 0

            # title
            f.write("***Table***\n\n")

            # header line
            headers = list(df.columns.values)
            line = " | "
            line2 = "|"
            for item in headers:
                line += str(item) + " | "
                line2 += "---:|"
            f.write(line + '\n')
            f.write(line2 + '\n')

            # data
            for row in df.itertuples():
                counter += 1
                line = " | "
                for item in row:
                    line += str(item) + " | "
                f.write(line + '\n')
                export_progress = int(100 * (counter/size))
                self.signals.progress.emit(export_progress)
                time.sleep(0.001)

        self.signals.status.emit(False)


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, round_num):
        super().__init__()
        self._data = data
        self.round_num = round_num

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]

            if np.isreal(value) and not isinstance(value, bool):
                return f"{value:.{self.round_num}f}"  # temporary all numbers as float
            else:
                return str(value)

        if role == Qt.TextAlignmentRole:
            return Qt.AlignVCenter + Qt.AlignRight

        if role == Qt.ForegroundRole:
            if pd.isna(self._data.iloc[index.row(), index.column()]):
                return QtGui.QColor("red")

    def rowCount(self, index) -> int:
        # the length of csv file (rows)
        return self._data.shape[0]

    def columnCount(self, index) -> int:
        # length of csv file (columns)
        return self._data.shape[1]

    def headerData(self, section: int, orientation, role: int) -> str:
        # header data (first row and first column)
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                if isinstance(self._data.index[section], str):
                    return self._data.index[section]
                else:
                    return str(self._data.index[section] + 1)


class MainWindow(QtWidgets.QMainWindow):
    MaxRecentFiles = 5

    def __init__(self, app_title="CSV Viewer"):
        super().__init__()
        self.progress = QProgressBar()
        self.threadpool = QThreadPool()
        self.app_title = app_title
        self.setMinimumSize(600, 300)
        self.df = None
        self.round_num = 2
        self.recentFileActs = []

        # settings
        self.settings = QtCore.QSettings('CSV_Viewer', 'CSV_Viewer')
        self.round_num = self.settings.value('round_numbers', self.round_num, int)

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
        self.button_open.setEnabled(True)

        # summary action
        style_summary = self.toolbar.style()
        icon = style_summary.standardIcon(QStyle.SP_FileDialogListView)
        self.button_summary = QAction(icon, "Summary", self)
        self.button_summary.setShortcut('Ctrl+S')
        self.button_summary.setStatusTip("Show summary for the current file")
        self.button_summary.triggered.connect(self.onToolbarSummaryButtonClick)
        self.toolbar.addAction(self.button_summary)

        # info action
        style_info = self.toolbar.style()
        icon = style_info.standardIcon(QStyle.SP_FileIcon)
        self.button_info = QAction(icon, "Info", self)
        self.button_info.setShortcut('Ctrl+I')
        self.button_info.setStatusTip("Show summary for the current file")
        self.button_info.triggered.connect(self.onToolbarInfoButtonClick)
        self.toolbar.addAction(self.button_info)

        # resize action
        style_resize = self.toolbar.style()
        icon = style_resize.standardIcon(QStyle.SP_BrowserReload)
        self.button_resize = QAction(icon, "Resize columns", self)
        self.button_resize.setShortcut('Ctrl+R')
        self.button_resize.setStatusTip("Resize columns width to content")
        self.button_resize.triggered.connect(self.onResizeColumns)
        self.toolbar.addAction(self.button_resize)

        # export to xlsx action
        style_xlsx = self.toolbar.style()
        icon = style_xlsx.standardIcon(QStyle.SP_FileLinkIcon)
        self.button_xlsx = QAction(icon, "Xlsx", self)
        self.button_xlsx.setStatusTip("Export data to xlsx file")
        self.button_xlsx.triggered.connect(self.onExportXlsx)
        self.toolbar.addAction(self.button_xlsx)

        # export to sqlite action
        style_sqlite = self.toolbar.style()
        icon = style_sqlite.standardIcon(QStyle.SP_FileLinkIcon)
        self.button_sqlite = QAction(icon, "SQLite", self)
        self.button_sqlite.setStatusTip("Export data to SQLite database")
        self.button_sqlite.triggered.connect(self.onExportSQLite)
        self.toolbar.addAction(self.button_sqlite)

        # export to html action
        style_html = self.toolbar.style()
        icon = style_html.standardIcon(QStyle.SP_FileLinkIcon)
        self.button_html = QAction(icon, "HTML", self)
        self.button_html.setStatusTip("Export data to HTML file")
        self.button_html.triggered.connect(self.onExportHTML)
        self.toolbar.addAction(self.button_html)

        # export to CSV action
        style_csv = self.toolbar.style()
        icon = style_csv.standardIcon(QStyle.SP_FileLinkIcon)
        self.button_csv = QAction(icon, "CSV", self)
        self.button_csv.setStatusTip("Export data to CSV file")
        self.button_csv.triggered.connect(self.onExportCSV)
        self.toolbar.addAction(self.button_csv)

        # export to Markdown action
        style_mark = self.toolbar.style()
        icon = style_mark.standardIcon(QStyle.SP_FileLinkIcon)
        self.button_mark = QAction(icon, "Markdown", self)
        self.button_mark.setStatusTip("Export data to Markdown file")
        self.button_mark.triggered.connect(self.onExportMarkdown)
        self.toolbar.addAction(self.button_mark)

        # import data from world bank climate api
        style_api = self.toolbar.style()
        icon = style_api.standardIcon(QStyle.SP_DialogSaveButton)
        self.button_api = QAction(icon, "API", self)
        self.button_api.setStatusTip("Import data from World Bank Climate API")
        self.button_api.triggered.connect(self.onImportFromAPI)
        self.toolbar.addAction(self.button_api)
        self.button_api.setEnabled(True)

        # close action
        style_close = self.toolbar.style()
        icon = style_close.standardIcon(QStyle.SP_DialogCloseButton)
        self.button_close = QAction(icon, "Close", self)
        self.button_close.setShortcut('Ctrl+X')
        self.button_close.setStatusTip("Close CSV file...")
        self.button_close.triggered.connect(self.onToolbarCloseButtonClick)
        self.toolbar.addAction(self.button_close)

        # quit action
        self.button_quit = QAction("Quit", self)
        self.button_quit.setShortcut('Ctrl+Q')
        self.button_quit.setStatusTip("Quit application")
        self.button_quit.triggered.connect(self.close)

        # toolbar show/hide action
        self.button_tool = QAction("Show/Hide toolbar", self)
        self.button_tool.setShortcut('Ctrl+T')
        self.button_tool.setStatusTip("Show or hide toolbar")
        self.button_tool.triggered.connect(self.showToolbar)

        # remove NaN
        self.button_nan = QAction("Remove NaN", self)
        self.button_nan.setShortcut('Ctrl+R')
        self.button_nan.setStatusTip("Remove rows with missing values")
        self.button_nan.triggered.connect(self.onRemoveNaN)

        # settings action
        style_settings = self.toolbar.style()
        icon = style_settings.standardIcon(QStyle.SP_ComputerIcon)
        self.button_settings = QAction(icon, "Settings", self)
        self.button_settings.setStatusTip("Application settings")
        self.button_settings.triggered.connect(self.onSettings)
        self.toolbar.addAction(self.button_settings)
        self.button_settings.setEnabled(True)

        # about action
        style_about = self.toolbar.style()
        icon = style_about.standardIcon(QStyle.SP_FileDialogInfoView)
        self.button_about = QAction(icon, "About", self)
        self.button_about.setStatusTip("About application")
        self.button_about.triggered.connect(self.about)
        self.toolbar.addAction(self.button_about)
        self.button_about.setEnabled(True)

        self.setButtons(False)

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
        file_menu.addSeparator()
        file_menu.addAction(self.button_nan)
        file_menu.addSeparator()
        file_menu.addAction(self.button_settings)
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
        view_menu.addSeparator()
        view_menu.addAction(self.button_tool)

        export_menu = menu.addMenu("&Export")
        export_menu.addAction(self.button_xlsx)
        export_menu.addAction(self.button_sqlite)
        export_menu.addAction(self.button_html)
        export_menu.addAction(self.button_csv)
        export_menu.addAction(self.button_mark)

        import_menu = menu.addMenu("&Import")
        import_menu.addAction(self.button_api)

        help_menu = menu.addMenu("&Help")
        help_menu.addAction(self.button_about)

        self.updateRecentFileActions()

        # status bar
        self.my_status = QStatusBar(self)
        self.my_status.addPermanentWidget(self.progress)
        self.progress.hide()
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

    def onToolbarOpenButtonClick(self) -> None:
        """ Show open dialog """

        dlg = ParameterDialog()
        dlg.setWindowTitle("Open")
        if dlg.exec_():
            file_name = dlg.filename.text()
            separator = dlg.separator
            decimal = dlg.decimal
            header = dlg.header
            index = dlg.index
        else:
            file_name = None

        if file_name:
            self.saveRecent(file_name)
            self.open_csv_file(file_name, separator, decimal, header, index)

    def onOpenRecentFile(self, file_name: str, sep=',', decimal='.') -> None:
        """ Open file from recent list, show open dialog """

        dlg = ParameterDialog(file_name, sep, decimal)
        dlg.setWindowTitle("Open")
        if dlg.exec_():
            file_name = dlg.filename.text()
            separator = dlg.separator
            decimal = dlg.decimal
            header = dlg.header
            index = dlg.index
        else:
            file_name = None

        if file_name:
            self.saveRecent(file_name)
            self.open_csv_file(file_name, separator, decimal, header, index)

    def open_csv_file(self, file_name: str, sep=',', decimal=".", header=True, index=True) -> None:
        """ Open csv file, load to tableview, set statusbar, enable close icon"""
        try:
            if header:
                my_header = 'infer'
            else:
                my_header = None

            if index:
                my_index = 0
            else:
                my_index = False

            print(my_header, my_index)
            data = pd.read_csv(file_name, sep=sep, decimal=decimal, header=my_header, index_col=my_index)
            self.df = data
            self.model = TableModel(self.df, self.round_num)
            self.labelStatus.setText(f"Rows: {self.df.shape[0]} Cols: {self.df.shape[1]}")
            self.table.setModel(self.model)
            if data.shape[0] > 0:
                self.table.selectRow(0)

            self.setButtons(True)
            self.setWindowTitle(self.app_title + ": " + file_name)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f"Error loading the file:\n {file_name}")

    def setButtons(self, state: bool) -> None:
        """ Set state of buttons/actions """
        self.button_close.setEnabled(state)
        self.button_summary.setEnabled(state)
        self.button_info.setEnabled(state)
        self.button_resize.setEnabled(state)
        self.button_xlsx.setEnabled(state)
        self.button_sqlite.setEnabled(state)
        self.button_html.setEnabled(state)
        self.button_csv.setEnabled(state)
        self.button_nan.setEnabled(state)
        self.button_mark.setEnabled(state)

    def onResizeColumns(self) -> None:
        """Resize columns action, run from menu View->Resize columns"""
        self.table.resizeColumnsToContents()

    def onToolbarCloseButtonClick(self) -> None:
        """Clear tableview, set statusbar and disable toolbar close, summary and info icons"""
        self.table.setModel(None)
        self.df = None
        self.setButtons(False)
        self.setWindowTitle(self.app_title)
        self.labelStatus.setText("Rows: 0 Cols: 0")

    def onToolbarSummaryButtonClick(self) -> None:
        """Show Summary dialog"""
        dlg = SummaryDialog(self.df.describe())
        dlg.setWindowTitle("Summary")
        dlg.exec_()

    def onToolbarInfoButtonClick(self) -> None:
        """Show Info dialog"""
        # buf = io.StringIO()
        # self.df.info(buf=buf)
        # tmp = buf.getvalue()

        dlg = InfoDialog(self.df)
        dlg.setWindowTitle("Info")
        dlg.exec_()

    def onExportXlsx(self) -> None:
        """ Export data to xlsx file """
        file_name, _ = QFileDialog.getSaveFileName(self, 'Export to xlsx', '', ".xlsx(*.xlsx)")
        if file_name:
            self.df.to_excel(file_name, engine='xlsxwriter')

    def onExportSQLite(self) -> None:
        file_name, _ = QFileDialog.getSaveFileName(self, 'Export to sqlite db', '', ".sqlite(*.sqlite)")
        if file_name:
            engine = create_engine(f'sqlite:///{file_name}', echo=False)
            self.df.to_sql('csv_data', con=engine)

    def onExportHTML(self) -> None:
        """ Export data to HTML file """
        file_name, _ = QFileDialog.getSaveFileName(self, 'Export to HTML file', '', ".html(*.html)")
        if file_name:
            self.df.to_html(file_name)

    def onExportCSV(self) -> None:
        """ Export data to new CSV file """
        file_name, _ = QFileDialog.getSaveFileName(self, 'Export to CSV file', '', ".csv(*.csv)")
        if file_name:
            self.df.to_csv(file_name, sep=',', decimal='.')

    def onImportFromAPI(self) -> None:
        dlg = ApiDialog()
        dlg.setWindowTitle("Import a Data CSV via API")
        if dlg.exec_():
            file_name = dlg.filename.text()
            address = dlg.address.text()
        else:
            file_name = None

        if file_name and address:
            res, text = dataload.import_data_by_api(address)
            if res:
                with open(file_name, "w") as f:
                    f.write(text)
                self.onOpenRecentFile(file_name)
            else:
                QMessageBox.warning(self, "Error", text)

    def closeEvent(self, event) -> None:
        """ Quit application, ask user before """
        if not app_test:
            result = QMessageBox.question(
                self, self.app_title,
                "Are you sure you want to quit?",
                QMessageBox.Yes | QMessageBox.No,
            )

        if app_test or result == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def about(self) -> None:
        """ Show About dialog (info about application)"""
        dlg = AboutDialog()
        dlg.exec_()

    def openRecentFile(self) -> None:
        """ Open file from recent list action """
        action = self.sender()
        if action:
            self.onOpenRecentFile(action.data())

    def saveRecent(self, file_name) -> None:
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

    def updateRecentFileActions(self) -> None:
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

    def strippedName(self, fullFileName: str) -> str:
        """ Return only file name, without path"""
        return QFileInfo(fullFileName).fileName()

    def showToolbar(self):
        """ show / hide main toolbar"""
        if self.toolbar.isHidden():
            self.toolbar.show()
        else:
            self.toolbar.hide()

    def onSettings(self):
        """ Round numbers to """
        n, result = QInputDialog.getInt(self, "Settings", "Round numbers to:", self.round_num, 0, 10, 1)
        if result and n != self.round_num:
            self.round_num = n
            self.settings.setValue('round_numbers', self.round_num)
            if self.df.shape[0] > 0:
                index = self.table.currentIndex()
                self.model = TableModel(self.df, self.round_num)
                self.table.setModel(self.model)
                self.table.selectRow(index.row())

    def onRemoveNaN(self):
        """ Remove rows with missing values """
        if self.df.shape[0] > 0:
            button = QMessageBox.question(self, "Remove NaN", "Remove rows with missing values?")
            if button == QMessageBox.Yes:
                self.df.dropna(axis=0, how='any', inplace=True)
                self.model = TableModel(self.df, self.round_num)
                self.table.setModel(self.model)
                self.table.selectRow(0)
                self.labelStatus.setText(f"Rows: {self.df.shape[0]} Cols: {self.df.shape[1]}")

    def onExportMarkdown(self):
        """ export to markdown table in thread """
        file_name, _ = QFileDialog.getSaveFileName(self, 'Export to Markdown file', '', ".md(*.md)")
        if file_name:
            worker = MarkdownWorker(file_name, self.df)
            worker.signals.progress.connect(self.update_progress)
            worker.signals.status.connect(self.update_status)
            self.threadpool.start(worker)

    def update_progress(self, progress):
        self.progress.setValue(progress)

    def update_status(self, status):
        if status:
            self.progress.show()
        else:
            self.progress.hide()
