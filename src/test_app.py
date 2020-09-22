import pytest
import mainwindow


@pytest.fixture
def app(qtbot):
    win = mainwindow.MainWindow()
    qtbot.addWidget(win)
    win.show()
    qtbot.wait_for_window_shown(win)
    return win


def test_title(app):
    assert app.windowTitle() == "CSV Viewer"
