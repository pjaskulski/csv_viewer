import pytest
import mainwindow
import dataload


@pytest.fixture
def app(qtbot):
    win = mainwindow.MainWindow()
    qtbot.addWidget(win)
    win.show()
    qtbot.wait_for_window_shown(win)
    return win


def test_title(app):
    assert app.windowTitle() == "CSV Viewer"


def test_download():
    link = 'http://climatedataapi.worldbank.org/climateweb/rest/v1/country/cru/tas/year/POL.csv'
    result, text = dataload.import_data_by_api(link)
    assert result

