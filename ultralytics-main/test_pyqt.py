import pytest
import object
# 软件系统GUI测试文件
# 测试窗口是否正常显示
def test_login_window_show(qtbot):
    window = object.MAIN_WIN
    qtbot.addWidget(window)
    window.show()
    assert window.isVisible()
def test_register_window_show(qtbot):
    window = object.REGISTER_QWIDGET
    qtbot.addWidget(window)
    window.show()
    assert window.isVisible()
def test_main_window_show(qtbot):
    window = object.DETECTION_QWIDGET
    qtbot.addWidget(window)
    window.show()
    assert window.isVisible()

def test_auto_window_show(qtbot):
    window = object.AUTO_DETECTION_QWIDGET
    qtbot.addWidget(window)
    window.show()
    assert window.isVisible()

def test_check_window_show(qtbot):
    window = object.PER_CHECK_QWIDGET
    qtbot.addWidget(window)
    window.show()
    assert window.isVisible()

def test_window_infor_show(qtbot):
    window = object.SYSTEM_INFOR_QWIDGET
    qtbot.addWidget(window)
    window.show()
    assert window.isVisible()

def test_window_feedback_show(qtbot):
    window = object.FEEDBACK_QWIDGET
    qtbot.addWidget(window)
    window.show()
    assert window.isVisible()

def test_window_password_show(qtbot):
    window = object.DETECTION_PASSWORD_CHANGE
    qtbot.addWidget(window)
    window.show()
    assert window.isVisible()

def test_window_add_data_show(qtbot):
    window = object.DETECTION_ADD_DATA
    qtbot.addWidget(window)
    window.show()
    assert window.isVisible()



