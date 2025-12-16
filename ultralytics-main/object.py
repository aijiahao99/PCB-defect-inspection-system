from PyQt5.QtCore import Qt
import os

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox, QSizePolicy
import register,login,sys,feedback,detection,change,add,system,auto_detect
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
# 该文件用于实体化所有的窗口对象，方便全局调用
# 启用高DPI支持
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling,True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps,True)
# 应用初始化
APP = QApplication(sys.argv)
# 应用字体和大小（可修改）
APP.setFont(QFont('Microsoft YaHei', 8))
# Login 窗口
# 实体化对象
MAIN_WIN = QMainWindow()
# 固定窗口大小
MAIN_WIN.setFixedSize(550,370)
# 创建对象
LOGIN_WIN = login.Ui_MainWindow()
# 初始化文件内ui对象
LOGIN_WIN.setupUi(MAIN_WIN)
LOGIN_WIN.label_3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
LOGIN_WIN.centralwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
# Register 窗口
REGISTER_QWIDGET = QWidget()
REGISTER_QWIDGET.setFixedSize(530,390)
REGISTER_WIN = register.Ui_register_window()
# 初始化文件内ui对象
REGISTER_WIN.setupUi(REGISTER_QWIDGET)
# feedback窗口初始化
FEEDBACK_QWIDGET = QWidget()
FEEDBACK_QWIDGET.setFixedSize(520,260)
FEEDBACK_WIN = feedback.Ui_feedback_form()
FEEDBACK_WIN.setupUi(FEEDBACK_QWIDGET)
# 系统信息窗口实体化
SYSTEM_INFOR_QWIDGET = QWidget()
SYSTEM_INFOR_QWIDGET.setFixedSize(400,260)
SYSTEM_INFOR_WIN = system.Ui_sys_Form()
SYSTEM_INFOR_WIN.setupUi(SYSTEM_INFOR_QWIDGET)
# detection 窗口初始化
# 重写closeevent函数，外部绑定新的closeevent函数
def closeEvent(event):
    answer_text = QMessageBox.question(
        None,
        "Exit Confirmation",
        "Confirm if you want to exit",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    if answer_text == QMessageBox.Yes:
        event.accept()
    else:
        event.ignore()

DETECTION_QWIDGET = QWidget()
DETECTION_QWIDGET.setFixedSize(930,660)
DETECTION_WIN = detection.Ui_system_form()
DETECTION_WIN.setupUi(DETECTION_QWIDGET)
DETECTION_QWIDGET.closeEvent = closeEvent
# 密码修改窗口初始化
DETECTION_PASSWORD_CHANGE = QWidget()
DETECTION_PASSWORD_CHANGE.setFixedSize(500,250)
DETECTION_PASSWORD_CHANGE_WIN = change.Ui_Modification()
DETECTION_PASSWORD_CHANGE_WIN.setupUi(DETECTION_PASSWORD_CHANGE)
# 添加数据窗口初始化
DETECTION_ADD_DATA = QWidget()
DETECTION_ADD_DATA.setFixedSize(660,250)
DETECTION_ADD_DATA_WIN = add.Ui_Form()
DETECTION_ADD_DATA_WIN.setupUi(DETECTION_ADD_DATA)
# 批量处理窗口初始化
AUTO_DETECTION_QWIDGET = QWidget()
AUTO_DETECTION_QWIDGET.setFixedSize(780,630)
AUTO_DETECTION_WIN = auto_detect.Ui_Batch_form()
AUTO_DETECTION_WIN.setupUi(AUTO_DETECTION_QWIDGET)
AUTO_DETECTION_QWIDGET.closeEvent = closeEvent

