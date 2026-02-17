import ast
import os.path
import sys
from datetime import datetime

import PyQt5
import cv2
import requests,service
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QCloseEvent

import object
from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QMessageBox, QFileDialog,
                             QGraphicsScene, QGraphicsPixmapItem, QWidget, QTableWidgetItem)
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import string
from openai import OpenAI
# 该文件用于初始化和构建系统界面功能函数
# 登入功能模块
class Login_fun:
    def __init__(self):
        # 登入按钮绑定事件
        object.LOGIN_WIN.login_but.clicked.connect(self.action_login)
        # 注册按钮绑定事件
        object.LOGIN_WIN.register_but.clicked.connect(self.action_register)
        object.LOGIN_WIN.sys_infor.triggered.connect(self.action_open)
        object.LOGIN_WIN.exit.triggered.connect(self.exit_system)
        object.LOGIN_WIN.feedback.triggered.connect(self.action_feedback)
        object.LOGIN_WIN.input_password_line.setEchoMode(PyQt5.QtWidgets.QLineEdit.Password)

    # 重置窗口
    def reset_window(self):
        object.LOGIN_WIN.input_username_line.clear()
        object.LOGIN_WIN.input_password_line.clear()

    # 打开系统信息窗口
    def action_open(self):
        object.SYSTEM_INFOR_QWIDGET.show()
    # 用户反馈模块
    def action_feedback(self):
        object.FEEDBACK_QWIDGET.show()
        object.MAIN_WIN.close()
    # 退出系统
    def exit_system(self):
        sys.exit(object.APP.exec_())

    # 登入系统模块
    def action_login(self):
        # 传入到flask服务端
        login_infor = {"username":object.LOGIN_WIN.input_username_line.text(),"password":object.LOGIN_WIN.input_password_line.text()}
        response = requests.post("http://127.0.0.1:5050/login",json=login_infor)
        if response.json().get('status') == "100":
            QMessageBox.warning(object.REGISTER_QWIDGET, "Warning", response.json().get('error'))
        else:
            # 动态刷新检测窗口
            reply = requests.post("http://127.0.0.1:5050/main_window")
            if reply.json().get('status') == '100':
                # 如果是普通用户则隐藏数据库管理端口
                object.DETECTION_WIN.funpage.setTabEnabled(2,False)
            else:
                object.DETECTION_WIN.funpage.setTabEnabled(2,True)

            if object.LOGIN_WIN.input_password_line.text() == 'admin' and object.LOGIN_WIN.input_username_line.text() == 'admin':
                object.DETECTION_WIN.change_password.setEnabled(False)
                object.DETECTION_WIN.cancel_account.setEnabled(False)
                object.DETECTION_WIN.feedback_but_2.setEnabled(False)
            else:
                object.DETECTION_WIN.change_password.setEnabled(True)
                object.DETECTION_WIN.cancel_account.setEnabled(True)
                object.DETECTION_WIN.feedback_but_2.setEnabled(True)
            # 初始化功能模块 （检测界面）
            object.DETECTION_WIN.toolBox.setCurrentIndex(0)
            get_path = requests.post("http://127.0.0.1:5050/get_default_path")
            object.DETECTION_WIN.result_save_pathline.setText(get_path.json().get('path'))
            object.DETECTION_WIN.search_board.hide()
            object.DETECTION_QWIDGET.show()
            object.DETECTION_WIN.username_display.setText(object.LOGIN_WIN.input_username_line.text())
            object.DETECTION_WIN.email_display.setText(response.json().get('address'))
            object.DETECTION_WIN.type_display.setText(response.json().get('level'))
            object.DETECTION_WIN.num_time_display.setText(str(response.json().get('times')))
            self.reset_window()
            object.MAIN_WIN.close()


    # 注册系统模块
    def action_register(self):
        object.MAIN_WIN.close()
        object.REGISTER_QWIDGET.show()

# 系统信息窗口
class Sys_infor:
    def __init__(self):
        self.files_count = 0
        self.count_py_files()
        # 更新系统信息
        object.SYSTEM_INFOR_WIN.plainTextEdit.setPlainText("*** Current system version number - English v3.0\n"
                                                           f"** The current number of system files - {self.files_count}\n"
                                                           f"** System developer - Jiahao Ai\n"
                                                           f"** Department - Information Systems and Technologies\n"
                                                           f"** System architecture - Single-core hybrid architecture\n"
                                                           f"** System version - Development")
    # 获取当前路径
    def get_current_path(self):
        current_path = os.getcwd()
        print(current_path)
        return '../' + current_path.split('\\')[-1] + '/'

    # 统计当前系统路径下的py文件
    def count_py_files(self):
        path = self.get_current_path()
        print(path)
        for root,_, files in os.walk(path):
            for file in files:
                if file.endswith(".py"):
                    self.files_count += 1

# 注册功能模块
class Register_fun:
    def __init__(self):
        # 初始化相关绑定函数和参数
        self.valid_code = None
        self.auto_generate_code()
        #print(self.valid_code)
        object.REGISTER_WIN.back_but.clicked.connect(self.action_back)
        object.REGISTER_WIN.renew_but.clicked.connect(self.action_refresh)
        object.REGISTER_WIN.confirm_but.clicked.connect(self.action_submit)

    # 重置窗口
    def reset_window(self):
        object.REGISTER_WIN.register_username_input.clear()
        object.REGISTER_WIN.register_password_input.clear()
        object.REGISTER_WIN.register_address_input.clear()
        self.auto_generate_code()
        object.REGISTER_WIN.code_input.clear()

    # 注册功能
    def action_submit(self):
        # 判断用户名和密码,邮箱, 用户类别是否为空
        if len(object.REGISTER_WIN.register_username_input.text()) == 0 or len(object.REGISTER_WIN.register_password_input.text()) == 0:
            QMessageBox.warning(object.REGISTER_QWIDGET, "Warning", "Missing username or password")
        elif len(object.REGISTER_WIN.register_address_input.text()) == 0:
            QMessageBox.warning(object.REGISTER_QWIDGET, "Warning", "Missing email address")
        # 如果验证码不同，则重新刷新并且清空信息
        elif object.REGISTER_WIN.code_input.text().lower() != self.valid_code.lower():
            QMessageBox.warning(object.REGISTER_QWIDGET, "Warning", "The verification code is incorrect")
            self.auto_generate_code()
            object.REGISTER_WIN.code_input.clear()
        else:#如果信息完整，传入flask调用sql脚本功能进行验证
            register_infor = {"username":object.REGISTER_WIN.register_username_input.text(),"password":object.REGISTER_WIN.register_password_input.text(),"address":object.REGISTER_WIN.register_address_input.text(),"type":"User"}
            response = requests.post("http://127.0.0.1:5050/register", json=register_infor)
            if response.json().get('status') != "100":
                QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", "Registration successful Log in again")
                object.MAIN_WIN.show()
                self.reset_window()
                object.REGISTER_QWIDGET.close()
                '''
                单通道登录注册代码
                object.DETECTION_WIN.funpage.removeTab(2)
                object.DETECTION_WIN.toolBox.setCurrentIndex(0)
                object.DETECTION_WIN.search_board.hide()
                object.DETECTION_QWIDGET.show()
                response = requests.post("http://127.0.0.1:5050/get_default_path")
                object.DETECTION_WIN.result_save_pathline.setText(response.json().get('path'))
                object.DETECTION_WIN.username_display.setText(object.REGISTER_WIN.register_username_input.text())
                object.DETECTION_WIN.type_display.setText("User")
                object.DETECTION_WIN.email_display.setText(object.REGISTER_WIN.register_address_input.text())
                object.DETECTION_WIN.num_time_display.setText('1')
                object.REGISTER_QWIDGET.close()
                self.reset_window()
                '''
            else:
                QMessageBox.warning(object.REGISTER_QWIDGET, "Warning", response.json().get('error'))
                self.auto_generate_code()
                object.REGISTER_WIN.code_input.clear()


    # 刷新验证码图片
    def action_refresh(self):
        self.auto_generate_code()

    # 后退
    def action_back(self):
        self.reset_window()
        object.REGISTER_QWIDGET.close()
        object.MAIN_WIN.show()

    # 生成随机验证码字符
    def random_text(self):
        return ''.join(random.choices((string.ascii_letters + string.digits), k=4))
    # 生成随机颜色
    def random_color(self):
        return (random.randint(0, 255), random.randint(0,255), random.randint(0,255))
    # 生成验证码图片模块
    def auto_generate_code(self):
        image = Image.new('RGB',(180,60),self.random_color())
        draw_img = ImageDraw.Draw(image)
        font = ImageFont.truetype("arial.ttf", 40)
        self.valid_code = self.random_text()
        # 绘制验证码字符
        for i, char in enumerate(self.valid_code):
            x = 40 * i + 10
            y = random.randint(0, 10)
            draw_img.text((x, y), char, font=font, fill=self.random_color())
        # 添加干扰点
        for _ in range(300):
            x = random.randint(0, 180)
            y = random.randint(0, 60)
            draw_img.point((x, y), fill=self.random_color())

        # 模糊处理
        image = image.filter(ImageFilter.BLUR)
        # 保存
        image.save("bd/code.jpg")
        # 设置图片
        object.REGISTER_WIN.code_imgs.setPixmap(QPixmap("bd/code.jpg"))

# 用户反馈界面功能模块
current_index = 0
class Feedback_fun:
    def __init__(self):
        # 控件绑定功能函数
        object.FEEDBACK_WIN.back_but_login.clicked.connect(self.action_back)
        object.FEEDBACK_WIN.submit_but.clicked.connect(self.action_submit)

    # 重置窗口
    def reset_window(self):
        object.FEEDBACK_WIN.name_line.clear()
        object.FEEDBACK_WIN.feedback_line.clear()
    # 用户反馈信息提交
    def action_submit(self):
        feedback_infor = {"name":object.FEEDBACK_WIN.name_line.text(),"content":object.FEEDBACK_WIN.feedback_line.toPlainText()}
        response = requests.post("http://127.0.0.1:5050/feedback", json=feedback_infor)
        if response.json().get('status') != "100":
            QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", "Submission successful")
            object.FEEDBACK_WIN.feedback_line.clear()
        else:
            QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", response.json().get('error'))

    # 返回登入界面
    def action_back(self):
        global current_index
        if current_index == 0:
            object.MAIN_WIN.show()
            object.FEEDBACK_QWIDGET.close()
            self.reset_window()
        else:
            object.FEEDBACK_WIN.name_line.setEnabled(True)
            self.reset_window()
            object.DETECTION_QWIDGET.show()
            object.FEEDBACK_QWIDGET.close()
            current_index = 0


# 检测界面功能模块
class Detect_mainwindow:
    def __init__(self):
        # 上传图片地址
        self.input_name = None
        # 图片的尺寸
        self.img_height = None
        self.img_width = None
        # 临时存储的搜索信息
        self.dataset = []
        # 原始图片地址
        self.img_org = None
        # 结果图片地址
        self.img_output = None
        # 选择的数据集
        self.data = []
        # 选择的行
        self.row = 0
        # 选择的列
        self.col = []
        # 选择的行标题
        self.row_header = ""
        # 选择的列标题
        self.col_header = []
        # 原始数据集的字段
        self.labels_set = []
        # 原始中文数据集字段
        self.zn_labels_set = []
        # 选择的英语数据集字段
        self.en_header = []
        # 初始化剪贴板
        self.copy_board = QApplication.clipboard()
        # 初始化数据分析图片
        self.data_imgs = []
        # 初始化数据分析对象
        self.data_view = []


        object.DETECTION_WIN.upload_img_but.clicked.connect(self.action_upload_img)
        object.DETECTION_WIN.detect_img_but.clicked.connect(self.action_detect_img)
        object.DETECTION_WIN.next_but.clicked.connect(self.action_next)
        object.DETECTION_WIN.open_camera_but.clicked.connect(self.action_real_time)
        object.DETECTION_WIN.download_report.clicked.connect(self.action_download)
        object.DETECTION_WIN.search_but.clicked.connect(self.action_search)
        object.DETECTION_WIN.pushButton.clicked.connect(self.action_data_show)

        object.DETECTION_WIN.next_search_but.clicked.connect(self.next_search)
        object.DETECTION_WIN.re_download.clicked.connect(self.re_download_report)
        object.DETECTION_WIN.change_password.clicked.connect(self.action_show_window)
        object.DETECTION_WIN.cancel_account.clicked.connect(self.action_delete_user)
        object.DETECTION_WIN.funpage.currentChanged.connect(self.database_init)
        object.DETECTION_WIN.reset_data.clicked.connect(self.action_set_data)
        object.DETECTION_WIN.delete_data_but.clicked.connect(self.action_delete_data)
        object.DETECTION_WIN.modify_data_but.clicked.connect(self.action_modify_data)
        object.DETECTION_WIN.add_data_but.clicked.connect(self.action_add_data)
        object.DETECTION_WIN.copy_but_1.clicked.connect(self.action_copy_product_id)
        object.DETECTION_WIN.copy_but_2.clicked.connect(self.action_copy_search_product_id)
        object.DETECTION_WIN.copy_but_3.clicked.connect(self.action_copy_search_report_id)
        object.DETECTION_WIN.paste_but.clicked.connect(self.action_paste_text)
        object.DETECTION_WIN.checkBox_2.stateChanged.connect(self.if_mult_selected)
        object.DETECTION_WIN.batch_detect_but.clicked.connect(self.action_open_auto)
        object.DETECTION_WIN.back_but_page3.clicked.connect(self.action_back_page3)
        object.DETECTION_WIN.left_but.setEnabled(False)
        object.DETECTION_WIN.right_but.clicked.connect(self.action_right_review)
        object.DETECTION_WIN.left_but.clicked.connect(self.action_left_review)
        object.DETECTION_WIN.data_table_name.currentIndexChanged.connect(self.on_self_changed)
        object.DETECTION_WIN.reload_but.clicked.connect(self.action_reload_data)
        object.DETECTION_WIN.switch_account_but.clicked.connect(self.action_switch_account)
        object.DETECTION_WIN.feedback_but_2.clicked.connect(self.action_open_feedback)
        object.DETECTION_WIN.sys_infor_but.clicked.connect(self.action_open_sys_infor)
        object.DETECTION_WIN.add_data_but.setEnabled(False)
        object.DETECTION_WIN.modify_data_but.setEnabled(False)
        object.DETECTION_WIN.delete_data_but.setEnabled(False)
        object.DETECTION_WIN.detect_img_but.setEnabled(False)
        object.DETECTION_WIN.checkBox_2.setEnabled(False)
        object.DETECTION_WIN.pushButton.setEnabled(False)
        object.DETECTION_WIN.copy_but_1.setEnabled(False)
        object.DETECTION_WIN.clean_but.setEnabled(False)
        object.DETECTION_WIN.assessment_but.setEnabled(False)
        object.DETECTION_WIN.assessment_but.clicked.connect(self.action_call_api_assessment)
        object.DETECTION_WIN.send_but.clicked.connect(self.action_call_api)
        object.DETECTION_WIN.clean_but.clicked.connect(self.action_clean_chat)
        object.DETECTION_WIN.back_but.clicked.connect(self.action_back_index1)
        object.DETECTION_WIN.reevaluation_but.clicked.connect(self.action_evaluation)
        object.DETECTION_WIN.user_textline.setPlaceholderText("Send the question you want to consult to the AI...")
        object.DETECTION_WIN.model_type.addItems(['deepseek-v3.2','qwen-flash-2025-07-28','qwen-plus','qwen-turbo'])
        object.DETECTION_WIN.model_box.addItems(['deepseek-v3.2','qwen-flash-2025-07-28','qwen-plus','qwen-turbo'])
        object.DETECTION_WIN.model_box.setCurrentIndex(1)
        object.DETECTION_WIN.model_type.setCurrentIndex(0)
        object.DETECTION_WIN.answer_textline.setPlaceholderText(
            f"Hello, I'm {object.DETECTION_WIN.model_type.currentText()} , Enter the question you want to ask")
        object.DETECTION_WIN.mode_box.addItems(['Product serial number', 'Report serial number'])
        object.DETECTION_WIN.mode_box.setCurrentIndex(0)
        # 修改序列号字体颜色
        object.DETECTION_WIN.product_number.setStyleSheet("""QLineEdit:disabled {
                                                        color: black; font_weight: bold;
                                                            }""")
        object.DETECTION_WIN.search_id.setStyleSheet("""QLineEdit:disabled {
                                                                color: black; font_weight: bold;
                                                                    }""")
        object.DETECTION_WIN.search_report_id.setStyleSheet("""QLineEdit:disabled {
                                                                color: black; font_weight: bold;
                                                                    }""")
        object.DETECTION_WIN.table_data.clicked.connect(self.action_cell_changed)
        object.DETECTION_WIN.model_type.currentIndexChanged.connect(self.action_update_api)

    # 切换账号
    def action_switch_account(self):
        self.reset_window()
        object.DETECTION_QWIDGET.hide()
        object.MAIN_WIN.show()
        self.action_clean_chat()
        object.DETECTION_WIN.stackedWidget_detection.setCurrentIndex(0)
    # 返回检测界面
    def action_back_index1(self):
        object.DETECTION_WIN.suggestion_but.clear()
        object.DETECTION_WIN.stackedWidget_detection.setCurrentIndex(0)
    # 重新调用api评估
    def action_evaluation(self):
        object.DETECTION_WIN.suggestion_but.clear()
        self.action_call_api_assessment()
    # 打开反馈界面
    def action_open_feedback(self):
        global current_index
        object.FEEDBACK_QWIDGET.show()
        object.FEEDBACK_WIN.name_line.setText(object.DETECTION_WIN.username_display.text())
        object.FEEDBACK_WIN.name_line.setEnabled(False)
        object.DETECTION_QWIDGET.hide()
        current_index += 1

    # 模型切换
    def action_update_api(self):
        self.action_clean_chat()
        object.DETECTION_WIN.answer_textline.setPlaceholderText(
            f"Hello, I'm {object.DETECTION_WIN.model_type.currentText()} , Enter the question you want to ask")

    # 调用API模型反馈结果
    def action_call_api_assessment(self):
        result_array = []
        result_array.append(object.DETECTION_WIN.items1.text())
        result_array.append(object.DETECTION_WIN.items2.text())
        result_array.append(object.DETECTION_WIN.items3.text())
        result_array.append(object.DETECTION_WIN.items4.text())
        result_array.append(object.DETECTION_WIN.items5.text())
        result_array.append(object.DETECTION_WIN.items6.text())
        data = {"result_line": str(result_array),
                'model_name': object.DETECTION_WIN.model_box.currentText()}
        reply = requests.post("http://127.0.0.1:5050/call_api_model_assessment", json=data)
        if reply.json().get('status') == 'pass':
            object.DETECTION_WIN.suggestion_but.setPlainText(reply.json().get('answer_text'))
            object.DETECTION_WIN.stackedWidget_detection.setCurrentIndex(1)
    # 删除ai对话内容
    def action_clean_chat(self):
        object.DETECTION_WIN.user_textline.clear()
        object.DETECTION_WIN.answer_textline.clear()
        object.DETECTION_WIN.clean_but.setEnabled(False)


    # 调用api模型
    def action_call_api(self):
        if len(object.DETECTION_WIN.user_textline.toPlainText()) == 0:
            QMessageBox.information(object.DETECTION_QWIDGET, "Attention", "The content of the text box is empty")
            return
        data = {"text_line": object.DETECTION_WIN.user_textline.toPlainText(),'model_name':object.DETECTION_WIN.model_type.currentText()}
        object.DETECTION_WIN.answer_textline.appendPlainText("User: " + object.DETECTION_WIN.user_textline.toPlainText())
        object.DETECTION_WIN.answer_textline.update()
        object.DETECTION_WIN.user_textline.clear()
        object.DETECTION_WIN.user_textline.setEnabled(False)
        object.DETECTION_WIN.user_textline.update()
        reply = requests.post("http://127.0.0.1:5050/call_api_model", json=data)
        if reply.json().get('status') == 'pass':
            object.DETECTION_WIN.answer_textline.appendPlainText("AI: " + reply.json().get('answer_text'))
        object.DETECTION_WIN.user_textline.setEnabled(True)
        object.DETECTION_WIN.clean_but.setEnabled(True)
        object.DETECTION_WIN.answer_textline.appendPlainText(f"-----Conversation time--------{datetime.now()}" + "\n")


    # 打开系统信息界面
    def action_open_sys_infor(self):
        object.SYSTEM_INFOR_QWIDGET.show()

    # 监听数据表选择
    def on_self_changed(self):
        object.DETECTION_WIN.delete_data_but.setEnabled(False)
        object.DETECTION_WIN.add_data_but.setEnabled(False)
        object.DETECTION_WIN.modify_data_but.setEnabled(False)
        object.DETECTION_WIN.pushButton.setEnabled(False)
        object.DETECTION_WIN.user_record_number.setText('')
        object.DETECTION_WIN.table_data.clear()
        object.DETECTION_WIN.checkBox_2.setChecked(False)
        object.DETECTION_WIN.checkBox_2.setEnabled(False)

    # 重置窗口
    def reset_window(self):
        self.next_search()
        self.action_next()
        object.DETECTION_WIN.items1.setText('')
        object.DETECTION_WIN.items2.setText('')
        object.DETECTION_WIN.items3.setText('')
        object.DETECTION_WIN.items4.setText('')
        object.DETECTION_WIN.items5.setText('')
        object.DETECTION_WIN.items6.setText('')
        object.DETECTION_WIN.img_name.clear()
        object.DETECTION_WIN.img_size.clear()
        object.DETECTION_WIN.img_type.clear()
        object.DETECTION_WIN.final_result.clear()
        object.DETECTION_WIN.product_number.clear()


    # 重新加载数据
    def action_reload_data(self):
        self.action_data_show()
        QMessageBox.information(object.DETECTION_QWIDGET, "Attention", "Refresh successful")

    # 打开批量检测窗口
    def action_open_auto(self):
        object.AUTO_DETECTION_QWIDGET.show()
        object.DETECTION_QWIDGET.hide()

    # 监听数据表
    def action_cell_changed(self):
        if object.DETECTION_WIN.checkBox_2.isChecked():
            object.DETECTION_WIN.checkBox_2.setChecked(False)

    # 控制数据分析页面向左
    def action_left_review(self):
        current_index = object.DETECTION_WIN.review_bd.currentIndex()
        if current_index != 0:
            object.DETECTION_WIN.review_bd.setCurrentIndex(current_index - 1)
            object.DETECTION_WIN.right_but.setEnabled(True)
        if current_index - 1 == 0:
            object.DETECTION_WIN.left_but.setEnabled(False)
            object.DETECTION_WIN.right_but.setEnabled(True)

    # 控制数据分析页面向右
    def action_right_review(self):
        current_index = object.DETECTION_WIN.review_bd.currentIndex()
        if current_index != 3:
            object.DETECTION_WIN.review_bd.setCurrentIndex(current_index + 1)
            self.show_images(self.data_view[current_index + 1],self.data_imgs[current_index + 1])
            object.DETECTION_WIN.left_but.setEnabled(True)
        if current_index + 1 == 3:
            object.DETECTION_WIN.right_but.setEnabled(False)
            object.DETECTION_WIN.left_but.setEnabled(True)

    # 判断是否全选择
    def if_mult_selected(self):
        if object.DETECTION_WIN.checkBox_2.isChecked():
            object.DETECTION_WIN.table_data.selectAll()
        else:
            object.DETECTION_WIN.table_data.clearSelection()

    # 显示图片
    def show_images(self,view, img_path):
        pix_map = QPixmap(img_path)
        item = QGraphicsPixmapItem(pix_map)
        scene = QGraphicsScene()
        scene.addItem(item)
        scene.setSceneRect(item.boundingRect())
        view.setScene(scene)
        view.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)

    # 移除数据分析窗口存在的图片
    def remove_exists_imgs(self,view):
        scene = view.scene()
        if not scene:
            return
        for i in scene.items():
            if isinstance(i,QGraphicsPixmapItem):
                scene.removeItem(i)

    # 数据分析窗口切换
    def action_data_show(self):
        object.DETECTION_WIN.stackedWidget.setCurrentIndex(1)
        if len(self.data_imgs) != 0:
            for _ in self.data_view:
                self.remove_exists_imgs(_)
            self.data_view.clear()
            self.data_imgs.clear()
            object.DETECTION_WIN.review_bd.setCurrentIndex(0)

        reply = requests.post("http://127.0.0.1:5050/data_review")
        if reply.json().get('status') == 'pass':
            self.data_imgs.append(reply.json().get('imgs1'))
            self.data_imgs.append(reply.json().get('imgs2'))
            self.data_imgs.append(reply.json().get('imgs3'))
            self.data_imgs.append(reply.json().get('imgs4'))
            self.data_view.append(object.DETECTION_WIN.graphicsView1)
            self.data_view.append(object.DETECTION_WIN.graphicsView2)
            self.data_view.append(object.DETECTION_WIN.graphicsView3)
            self.data_view.append(object.DETECTION_WIN.graphicsView4)
            self.show_images(object.DETECTION_WIN.graphicsView1, reply.json().get('imgs1'))
            #self.show_images(object.DETECTION_WIN.graphicsView2, reply.json().get('imgs2'))

        

    # 切换回去数据库界面
    def action_back_page3(self):
        object.DETECTION_WIN.stackedWidget.setCurrentIndex(0)

    # 粘贴字符串
    def action_paste_text(self):
        object.DETECTION_WIN.input_product_id.setText(self.copy_board.text())

    # 复制搜索报告序列号字符串
    def action_copy_search_report_id(self):
        if object.DETECTION_WIN.search_report_id.text() != 'None':
            self.copy_board.setText(object.DETECTION_WIN.search_report_id.text())
            QMessageBox.information(object.DETECTION_QWIDGET, "Attention", "Copy successful")
        else:
            QMessageBox.information(object.DETECTION_QWIDGET, "Attention", "Copy failed")

    # 复制搜索产品序列号字符串
    def action_copy_search_product_id(self):
        self.copy_board.setText(object.DETECTION_WIN.search_id.text())
        QMessageBox.information(object.DETECTION_QWIDGET, "Attention", "Copy successful")

    # 复制产品序列号字符串
    def action_copy_product_id(self):
        self.copy_board.setText(object.DETECTION_WIN.product_number.text())
        QMessageBox.information(object.DETECTION_QWIDGET, "Attention", "Copy successful")

    # 打开添加数据窗口
    def action_add_data(self):
        object.DETECTION_ADD_DATA_WIN.table_add_data.setRowCount(1)
        object.DETECTION_ADD_DATA_WIN.table_add_data.setColumnCount(len(self.labels_set) - 1)
        # 初始化行和列
        tmp_set = []
        for i in range(len(self.labels_set)):
            tmp_set.append("")
        # 导入数据表中
        for i, data in enumerate(tmp_set):
            for j, value in enumerate(data):
                items = QTableWidgetItem(value)
                object.DETECTION_ADD_DATA_WIN.table_add_data.setItem(i, j, items)

        object.DETECTION_ADD_DATA_WIN.table_add_data.setHorizontalHeaderLabels(self.labels_set[1:])
        object.DETECTION_ADD_DATA.show()
        object.DETECTION_QWIDGET.hide()

    # 处理数据表中选择的数据
    def processing_tabel_data(self):
        items = object.DETECTION_WIN.table_data.selectedItems()
        if len(items) == 0:
            QMessageBox.warning(object.DETECTION_QWIDGET, "Attention", "Unselected data")
            return False
        for i in range(len(items)):
            self.data.append(items[i].text())
            self.row = items[i].row()
            self.col.append(items[i].column())

            self.row_header = object.DETECTION_WIN.table_data.verticalHeaderItem(self.row).text() if object.DETECTION_WIN.table_data.verticalHeaderItem(self.row) else ""
            self.col_header.append(object.DETECTION_WIN.table_data.horizontalHeaderItem(self.col[i]).text() if object.DETECTION_WIN.table_data.horizontalHeaderItem(self.col[i]) else "")

            for j in range(len(self.zn_labels_set)):
                if self.zn_labels_set[j] == self.col_header[i]:
                    self.en_header.append(self.labels_set[j])
                    break
        #print(f"{self.row} , {self.col}")
        #print(f"{self.row_header},{self.col_header}")
        return True
    #修改选择的数据
    def action_modify_data(self):
        if object.DETECTION_WIN.checkBox_2.isChecked():
            QMessageBox.warning(object.DETECTION_QWIDGET, "Attention", "This operation is not supported")
            return
        if self.processing_tabel_data():
            if len(self.data) == 1 and self.col[0] != 0:
                input_data = {"header":self.en_header[0],"row_id":object.DETECTION_WIN.table_data.item(self.row,0).text(),"row_name":self.labels_set[0],"row_data":object.DETECTION_WIN.table_data.item(self.row,self.col[0]).text()}
                response = requests.post("http://127.0.0.1:5050/modify_database_data", json=input_data)
                if response.json().get('status') != '100':
                    QMessageBox.warning(object.DETECTION_QWIDGET, "Attention", response.json().get('infor'))
                    # 更新数据
                    self.action_set_data()

            else:
                QMessageBox.warning(object.DETECTION_QWIDGET, "Attention", "Cannot delete the primary key or multiple pieces of data")
            # 更新数据集
            self.data.clear()
            self.col.clear()
            self.col_header.clear()
            self.en_header.clear()

    # 删除选择的数据
    def action_delete_data(self):
        if object.DETECTION_WIN.checkBox_2.isChecked():
            response = requests.post("http://127.0.0.1:5050/delete_all")
            if response.json().get('status') != '100':
                QMessageBox.warning(object.DETECTION_QWIDGET, "Attention", response.json().get('infor'))
                object.DETECTION_WIN.table_data.clearSelection()
                # 更新数据
                self.action_set_data()
                self.on_self_changed()
                object.DETECTION_WIN.pushButton.setEnabled(False)
                if object.DETECTION_WIN.data_table_name.currentIndex() == 0:
                    QMessageBox.warning(object.DETECTION_QWIDGET, "Attention", "The current user account does not exist. Please log in again.")
                    sys.exit(object.APP.exec_())
                return

        elif self.processing_tabel_data():
            if len(self.data) == 1 and self.col[0] != 0:
                input_data = {"header":self.en_header[0],"row_id":object.DETECTION_WIN.table_data.item(self.row,0).text(),"row_name":self.labels_set[0]}
                response = requests.post("http://127.0.0.1:5050/delete_database_data", json=input_data)
                if response.json().get('status') != '100':
                    QMessageBox.warning(object.DETECTION_QWIDGET, "Attention", response.json().get('infor'))
                    # 更新数据
                    self.action_set_data()

            else:
                # 判断用户选择的是否为整行数据
                if len(self.en_header) == len(self.labels_set):
                    for i in range(len(self.en_header)):
                        if self.en_header[i] != self.labels_set[i]:
                            QMessageBox.warning(object.DETECTION_QWIDGET, "Attention", "This operation is not supported")
                            break

                    selected_data = {'row_id':self.data[0],'row_name':self.en_header[0]}
                    response = requests.post("http://127.0.0.1:5050/delete_row", json=selected_data)
                    if response.json().get('status') != '100':
                        QMessageBox.warning(object.DETECTION_QWIDGET, "Attention", "Deletion operation successful")
                        # 更新数据
                        self.action_set_data()
                    else:
                        QMessageBox.warning(object.DETECTION_QWIDGET, "Attention", "Deletion operation failed")
                    print(self.en_header[0])
                else:
                    QMessageBox.warning(object.DETECTION_QWIDGET, "Attention", "This operation is not supported")

            # 更新数据集
            self.data.clear()
            self.col.clear()
            self.col_header.clear()
            self.en_header.clear()


    # 上传和更新数据
    def action_set_data(self):
        if object.DETECTION_WIN.data_table_name.currentIndex() in [0,1]:
            object.DETECTION_WIN.pushButton.setEnabled(True)

        # 判断当前数据表是否存在数据
        for row in range(object.DETECTION_WIN.table_data.rowCount()):
            for col in range(object.DETECTION_WIN.table_data.columnCount()):
                item = object.DETECTION_WIN.table_data.item(row,col)
                if item and item.text().strip():
                    print("Exists data")
                    # 清除存在的数据
                    object.DETECTION_WIN.table_data.clearContents()
                    object.DETECTION_WIN.table_data.setRowCount(0)
                    object.DETECTION_WIN.user_record_number.setText('0')
                    break

        if len(self.labels_set) != 0:
            self.labels_set.clear()

        print(object.DETECTION_WIN.data_table_name.currentText())
        type_data = {"type":object.DETECTION_WIN.data_table_name.currentText()}
        response = requests.post("http://127.0.0.1:5050/get_database_data", json=type_data)
        if response.json().get('status') != '100':
            object.DETECTION_WIN.table_data.setRowCount(response.json().get('row'))
            object.DETECTION_WIN.table_data.setColumnCount(response.json().get('col'))
            raw_set = ast.literal_eval(response.json().get('set'))
            raw_labels = ast.literal_eval(response.json().get('labels'))
            self.zn_labels_set = ast.literal_eval(response.json().get('zn_labels'))
            # 处理原始数据
            new_set = []
            for i in range(len(raw_set)):
                new_set.append(list(map(str,raw_set[i])))

            for i in range(len(raw_labels)):
                self.labels_set.append(list(raw_labels[i])[0])

            object.DETECTION_WIN.table_data.setHorizontalHeaderLabels(self.zn_labels_set)
            object.DETECTION_WIN.add_data_but.setEnabled(True)
            object.DETECTION_WIN.modify_data_but.setEnabled(True)
            object.DETECTION_WIN.delete_data_but.setEnabled(True)
            object.DETECTION_WIN.checkBox_2.setEnabled(True)

            # 导入数据表中
            for i,data in enumerate(new_set):
                for j,value in enumerate(data):
                    items = QTableWidgetItem(value)
                    object.DETECTION_WIN.table_data.setItem(i,j,items)

            object.DETECTION_WIN.user_record_number.setText(str(response.json().get('row')))
        else:
            QMessageBox.warning(object.DETECTION_QWIDGET, "Attention", "The data is empty")

    # 数据库管理模块初始化
    def database_init(self):
        # 判断当前用户是否为管理员
        if object.DETECTION_WIN.funpage.currentIndex() == 2:
            if object.DETECTION_WIN.type_display.text() != 'User':
                if object.DETECTION_WIN.data_table_name.count() < 1:
                    object.DETECTION_WIN.data_table_name.addItems(['User data','Product data','Report data','Feedback data'])
                    object.DETECTION_WIN.data_table_name.setCurrentIndex(0)
        else:
            object.DETECTION_WIN.table_data.clear()
            object.DETECTION_WIN.delete_data_but.setEnabled(False)
            object.DETECTION_WIN.checkBox_2.setChecked(False)
            object.DETECTION_WIN.add_data_but.setEnabled(False)
            object.DETECTION_WIN.modify_data_but.setEnabled(False)
            object.DETECTION_WIN.pushButton.setEnabled(False)
            object.DETECTION_WIN.user_record_number.setText('')
            object.DETECTION_WIN.checkBox_2.setChecked(False)
            object.DETECTION_WIN.checkBox_2.setEnabled(False)




    # 删除用户当前账号
    def action_delete_user(self):
        reply = QMessageBox.information(object.DETECTION_QWIDGET, "Attention", "Do you want to cancel the current account?",QMessageBox.Yes | QMessageBox.No,QMessageBox.No)
        if reply == QMessageBox.Yes:
            response = requests.post("http://127.0.0.1:5050/delete_user")
            if response.json().get('status') != '100':
                QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", response.json().get('infor'))
                sys.exit(object.APP.exec_())
            else:
                QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", "An error occurred")

    # 打开界面
    def action_show_window(self):
        object.DETECTION_PASSWORD_CHANGE.show()
        object.DETECTION_PASSWORD_CHANGE_WIN.current_username.setText(object.DETECTION_WIN.username_display.text())
    # 重新下载报告
    def re_download_report(self):
        new_data = {"output":object.DETECTION_WIN.final_search_result.text(),"product_id":object.DETECTION_WIN.search_id.text(),
                    "dataset":str(self.dataset),"img1":self.img_org,"img2":self.img_output}
        response = requests.post("http://127.0.0.1:5050/re_download", json=new_data)
        if response.json().get('status') != 100:
            QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", "Download successful!")
            self.update_search_board(response.json().get('id'),response.json().get('time'))
        else:
            QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", "Download failed!")

    # 如果未下载的报告重新下载之后，会更新搜索信息
    def update_search_board(self, new_id, time):
        object.DETECTION_WIN.search_report_id.setText(new_id)
        object.DETECTION_WIN.search_report_time.setText(time)
        object.DETECTION_WIN.status_box.setText("Downloaded")

    # 继续搜索模块
    def next_search(self):
        object.DETECTION_WIN.search_board.hide()
        object.DETECTION_WIN.input_product_id.clear()
        object.DETECTION_WIN.search_but.setEnabled(True)
    # 判断图片是否在本地
    def if_img_path_exists(self,path):
        if os.path.exists(path):
            return True
        return False

    # 处理和显示搜索信息
    def transmit_data(self,img1,img2,result,num,time,report,download_time):
        object.DETECTION_WIN.final_search_result.setText(result)
        object.DETECTION_WIN.detect_search_time.setText(time)
        if object.DETECTION_WIN.mode_box.currentIndex() == 0:
            object.DETECTION_WIN.search_id.setText(object.DETECTION_WIN.input_product_id.text())

        object.DETECTION_WIN.status_box.setEnabled(False)
        if report == '':
            object.DETECTION_WIN.status_box.setText("Not downloaded")
            object.DETECTION_WIN.search_report_id.setText("None")
            object.DETECTION_WIN.search_report_time.setText("None")
        else:
            object.DETECTION_WIN.status_box.setText("Downloaded")
            object.DETECTION_WIN.search_report_id.setText(report)
            object.DETECTION_WIN.search_report_time.setText(download_time)

        num_list = ast.literal_eval(num)
        for i in range(len(num_list)):
            if num_list[i] == ' ':
                num_list[i] = 0

        self.dataset = num_list

        object.DETECTION_WIN.search_items1.setText(str(num_list[0]))
        object.DETECTION_WIN.search_items2.setText(str(num_list[1]))
        object.DETECTION_WIN.search_items3.setText(str(num_list[2]))
        object.DETECTION_WIN.search_items4.setText(str(num_list[3]))
        object.DETECTION_WIN.search_items5.setText(str(num_list[4]))
        object.DETECTION_WIN.search_items6.setText(str(num_list[5]))

        if self.if_img_path_exists(img1):
            pix_map1 = QPixmap(img1)
            item1 = QGraphicsPixmapItem(pix_map1)
            scene1 = QGraphicsScene()
            scene1.addItem(item1)
            object.DETECTION_WIN.search_input_img.setScene(scene1)
            object.DETECTION_WIN.search_input_img.fitInView(item1, Qt.KeepAspectRatio)
            self.img_org = img1


        if self.if_img_path_exists(img2):
            pix_map2 = QPixmap(img2)
            item2 = QGraphicsPixmapItem(pix_map2)
            scene2 = QGraphicsScene()
            scene2.addItem(item2)
            object.DETECTION_WIN.search_output_img.setScene(scene2)
            object.DETECTION_WIN.search_output_img.fitInView(item2, Qt.KeepAspectRatio)
            self.img_output = img2
            print(img2)

        object.DETECTION_WIN.search_but.setEnabled(False)



    # 搜索产品信息模块
    def action_search(self):
        # 判断信息是否为空
        if len(object.DETECTION_WIN.input_product_id.text()) == 0:
            QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", "The search information is empty")
            return

        if object.DETECTION_WIN.mode_box.currentIndex() == 0:
            search_id = {"id":object.DETECTION_WIN.input_product_id.text(),"mode":"product"}
        else:
            search_id = {"id":object.DETECTION_WIN.input_product_id.text(),"mode":"report"}

        response = requests.post("http://127.0.0.1:5050/search", json=search_id)
        if response.json().get('status') == '100':
            if response.json().get('mode') == 'product':
                QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", "Product information does not exist")
            else:
                QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", "Report information does not exist")
            return
        else:
            QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", "Query successful !")
            object.DETECTION_WIN.search_board.show()
            if object.DETECTION_WIN.mode_box.currentIndex() == 1:
                object.DETECTION_WIN.search_id.setText(response.json().get('product_id'))
            self.transmit_data(response.json().get('detect_img'), response.json().get('result_img'),
                               response.json().get('result'), response.json().get('defect_num'),
                               response.json().get('detect_time'), response.json().get('report_id'),
                               response.json().get('download'))


    # 下载报告
    def action_download(self):
        save_path = {"path":object.DETECTION_WIN.report_save_address.text(),"id":object.DETECTION_WIN.product_number.text()}
        response = requests.post("http://127.0.0.1:5050/download",json=save_path)
        if response.json().get('status') == "Pass":
            self.box = QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", "Report download successful")
        else:
            QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", "Incorrect file address")

    # 实时检测，打开摄像头
    def action_real_time(self):
        QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", "Press 'e' to exit the detection")
        response = requests.post("http://127.0.0.1:5050/camera")
        if response.json().get('status') == "Pass":
            QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", "Exit from real-time detection mode")

    # 刷新页面
    def action_next(self):
        # 清除存在的识别结果图片
        scene = object.DETECTION_WIN.output_img.scene()
        if scene and not scene.items() == []:
            scene.clear()

        # 清除存在的识别结果图片
        scene = object.DETECTION_WIN.input_img.scene()
        if scene and not scene.items() == []:
            scene.clear()

        object.DETECTION_WIN.toolBox.setCurrentIndex(0)
        object.DETECTION_WIN.download_report.setEnabled(False)
        object.DETECTION_WIN.detect_img_but.setEnabled(False)
        object.DETECTION_WIN.copy_but_1.setEnabled(False)
        object.DETECTION_WIN.assessment_but.setEnabled(False)
        service.reset_data()

    # 上传图片功能模块
    def action_upload_img(self):
        self.input_name, _ = QFileDialog.getOpenFileName(None, "select your imgs", "", "Image Files (*.png *.jpg *.bmp)")
        if self.input_name:
            pix_map = QPixmap(self.input_name)
            self.img_height = pix_map.height()
            self.img_width = pix_map.width()
            item = QGraphicsPixmapItem(pix_map)
            scene = QGraphicsScene()
            scene.addItem(item)
            object.DETECTION_WIN.input_img.setScene(scene)
            object.DETECTION_WIN.input_img.fitInView(item,Qt.KeepAspectRatio)
            # 清除存在的识别结果图片
            scene = object.DETECTION_WIN.output_img.scene()
            if scene and not scene.items() == []:
                scene.clear()

            service.reset_data()

            object.DETECTION_WIN.download_report.setEnabled(False)
            object.DETECTION_WIN.detect_img_but.setEnabled(True)
            object.DETECTION_WIN.assessment_but.setEnabled(False)
            object.DETECTION_WIN.items1.setText('')
            object.DETECTION_WIN.items2.setText('')
            object.DETECTION_WIN.items3.setText('')
            object.DETECTION_WIN.items4.setText('')
            object.DETECTION_WIN.items5.setText('')
            object.DETECTION_WIN.items6.setText('')
            object.DETECTION_WIN.img_name.clear()
            object.DETECTION_WIN.img_size.clear()
            object.DETECTION_WIN.img_type.clear()
            object.DETECTION_WIN.final_result.clear()
            object.DETECTION_WIN.product_number.clear()
            object.DETECTION_WIN.copy_but_1.setEnabled(False)

    # 更新结果
    def update_result_infor(self,data_set,result,imgn,imgt,path,id):
        object.DETECTION_WIN.img_name.setText(imgn)
        object.DETECTION_WIN.img_type.setText(imgt)
        object.DETECTION_WIN.final_result.setText(result)
        object.DETECTION_WIN.product_number.setText(id)
        object.DETECTION_WIN.report_save_address.setText(path)

        object.DETECTION_WIN.items1.setText(ast.literal_eval(data_set)[0][1])
        object.DETECTION_WIN.items2.setText(ast.literal_eval(data_set)[1][1])
        object.DETECTION_WIN.items3.setText(ast.literal_eval(data_set)[2][1])
        object.DETECTION_WIN.items4.setText(ast.literal_eval(data_set)[3][1])
        object.DETECTION_WIN.items5.setText(ast.literal_eval(data_set)[4][1])
        object.DETECTION_WIN.items6.setText(ast.literal_eval(data_set)[5][1])

        object.DETECTION_WIN.img_size.setText(str(self.img_width) + "x" + str(self.img_height))

    # 运行模型
    def action_detect_img(self):
        if not os.path.isdir(object.DETECTION_WIN.result_save_pathline.text()):
            QMessageBox.warning(object.DETECTION_ADD_DATA, "Attention","The save path does not exist")
            return

        if self.input_name is not None:
            input = {"address":self.input_name,'output_address':object.DETECTION_WIN.result_save_pathline.text()}
            response = requests.post("http://127.0.0.1:5050/model", json=input)
            if response.json().get('status') != '100':
                item = QGraphicsPixmapItem(QPixmap(response.json().get('address')))
                scene = QGraphicsScene()
                scene.addItem(item)
                object.DETECTION_WIN.output_img.setScene(scene)
                object.DETECTION_WIN.output_img.fitInView(item, Qt.KeepAspectRatio)

                self.update_result_infor(response.json().get('data_set'),response.json().get('result'),response.json().get('imgn'),response.json().get('imgt'),response.json().get('report_path'),response.json().get('id'))
                object.DETECTION_WIN.copy_but_1.setEnabled(True)
                object.DETECTION_WIN.toolBox.setCurrentIndex(1)
                object.DETECTION_WIN.download_report.setEnabled(True)
                object.DETECTION_WIN.assessment_but.setEnabled(True)

class Add_data:
    def __init__(self):
        self.labels = []
        object.DETECTION_ADD_DATA_WIN.back_but.clicked.connect(self.action_back)
        object.DETECTION_ADD_DATA_WIN.reset_data_but.clicked.connect(self.action_clean)
        object.DETECTION_ADD_DATA_WIN.confirm_data_but.clicked.connect(self.action_submit)

    # 提交到数据库
    def action_submit(self):
        data = []
        # 判断当前数据表是否存在空格
        for row in range(object.DETECTION_ADD_DATA_WIN.table_add_data.rowCount()):
            for col in range(object.DETECTION_ADD_DATA_WIN.table_add_data.columnCount()):
                item = object.DETECTION_ADD_DATA_WIN.table_add_data.item(row, col)
                if not item or item.text().strip() == "":
                    QMessageBox.warning(object.DETECTION_ADD_DATA, "Attention", "Spaces or blank cells are not allowed")
                    return
                data.append(item.text().strip())
        # 打包成字典类型
        add_data = dict()
        headers = [object.DETECTION_ADD_DATA_WIN.table_add_data.horizontalHeaderItem(i).text() if object.DETECTION_ADD_DATA_WIN.table_add_data.horizontalHeaderItem(i) else "" for i in range(object.DETECTION_ADD_DATA_WIN.table_add_data.columnCount())]

        for i in range(len(headers)):
            add_data[f"{headers[i]}"] = data[i]

        response = requests.post("http://127.0.0.1:5050/add_database_data", json=add_data)
        if response.json().get('status') != '100':
            QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", response.json().get('infor'))
            self.action_clean()
        else:
            QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", response.json().get('infor'))


    # 清空数据
    def action_clean(self):
        # 判断当前数据表是否存在数据
        for row in range(object.DETECTION_ADD_DATA_WIN.table_add_data.rowCount()):
            for col in range(object.DETECTION_ADD_DATA_WIN.table_add_data.columnCount()):
                item = object.DETECTION_ADD_DATA_WIN.table_add_data.item(row, col)
                if item and item.text().strip():
                    print("Exists data")
                    # 清除存在的数据
                    object.DETECTION_ADD_DATA_WIN.table_add_data.clearContents()
                    break
    # 返回界面
    def action_back(self):
        self.action_clean()
        object.DETECTION_ADD_DATA.close()
        object.DETECTION_QWIDGET.show()


class Password_modification:
    def __init__(self):
        object.DETECTION_PASSWORD_CHANGE_WIN.back_last_but.clicked.connect(self.action_back)
        object.DETECTION_PASSWORD_CHANGE_WIN.confirm_change_but.clicked.connect(self.action_confirm_change)

    # 重置窗口
    def reset_window(self):
        object.DETECTION_PASSWORD_CHANGE_WIN.new_input_password.clear()
        object.DETECTION_PASSWORD_CHANGE_WIN.confirm_new_password.clear()

    # 确认更改
    def action_confirm_change(self):
        data_set = {"username":object.DETECTION_PASSWORD_CHANGE_WIN.current_username.text(),"new_password":object.DETECTION_PASSWORD_CHANGE_WIN.new_input_password.text(),"confirm_password":object.DETECTION_PASSWORD_CHANGE_WIN.confirm_new_password.text()}
        response = requests.post("http://127.0.0.1:5050/change_password",json=data_set)
        if response.json().get('status') == 'Pass':
            QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", response.json().get('infor'))
            object.DETECTION_PASSWORD_CHANGE.close()
            sys.exit(object.APP.exec_())
        else:
            QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", response.json().get('error'))

    # 返回主界面
    def action_back(self):
        object.DETECTION_QWIDGET.show()
        object.DETECTION_PASSWORD_CHANGE.close()
        self.reset_window()

# 批量检测界面功能
class Auto_detection:
    def __init__(self):
        self.path_set = dict()
        object.AUTO_DETECTION_WIN.back_but.clicked.connect(self.action_back)
        object.AUTO_DETECTION_WIN.confirm_but.clicked.connect(self.action_confirm_path)
        object.AUTO_DETECTION_WIN.reset_but.clicked.connect(self.action_reset_path)
        object.AUTO_DETECTION_WIN.detect_but.clicked.connect(self.action_detect)
        object.AUTO_DETECTION_WIN.tabWidget.setTabEnabled(1,False)
        object.AUTO_DETECTION_WIN.reset_but.setEnabled(False)
        object.AUTO_DETECTION_WIN.result_check_but.setEnabled(False)
        object.AUTO_DETECTION_WIN.back_next_but.setEnabled(False)
        object.AUTO_DETECTION_WIN.result_check_but.clicked.connect(self.action_batch_result_review)
        object.AUTO_DETECTION_WIN.back_next_but.clicked.connect(self.action_clean_back)
        object.AUTO_DETECTION_WIN.next_page_but.clicked.connect(self.next_data_show)
        object.AUTO_DETECTION_WIN.previous_but.clicked.connect(self.last_data_show)
        object.AUTO_DETECTION_WIN.close_but.clicked.connect(self.action_exit)
        object.AUTO_DETECTION_WIN.copy_but.clicked.connect(self.action_copy)
        object.AUTO_DETECTION_WIN.continue_but.clicked.connect(self.continue_detect)
        object.AUTO_DETECTION_WIN.download_but.clicked.connect(self.download_current_report)
        object.AUTO_DETECTION_WIN.download_all_but.clicked.connect(self.download_all_report)
        object.AUTO_DETECTION_WIN.result_path.setPlainText('batch_detect/')
        object.AUTO_DETECTION_WIN.product_id_text.setStyleSheet("""QLineEdit:disabled {
                                                                color: black; font_weight: bold;
                                                                    }""")

        # 符合要求的图片类型
        self.regular = ['jpg', 'png', 'jpeg','JPG','PNG','JPEG']
        # 更新频率
        self.update_interval = 0
        # 数据集
        self.df_set = None
        # 初始化剪贴板
        self.copy_board = QApplication.clipboard()

    # 重置窗口
    def reset_window(self):
        self.action_reset_path()
        self.continue_detect()
        self.action_clean_back()

    # 下载所有报告
    def download_all_report(self):
        reply = requests.post("http://127.0.0.1:5050/batch_download_all_report")
        if reply.json().get('status') == 'pass':
            QMessageBox.warning(object.REGISTER_QWIDGET, "Attention",
                                "All reports have been downloaded successfully")

    # 下载当前的报告
    def download_current_report(self):
        download_index = str(int(object.AUTO_DETECTION_WIN.current_lcd.value()) - 1)
        reply = requests.post("http://127.0.0.1:5050/batch_download_report",json=download_index)
        if reply.json().get('status') == 'pass':
            QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", "The current report has been downloaded successfully")


    # 返回继续检测
    def action_clean_back(self):
        requests.post("http://127.0.0.1:5050/batch_result_clear")
        object.AUTO_DETECTION_WIN.tabWidget.setCurrentIndex(0)
        object.AUTO_DETECTION_WIN.tabWidget.setTabEnabled(0,True)
        object.AUTO_DETECTION_WIN.tabWidget.setTabEnabled(1, False)
        object.AUTO_DETECTION_WIN.status_progressBar.setValue(0)
        object.AUTO_DETECTION_WIN.status_label.setText("In the process of detection...")
        object.AUTO_DETECTION_WIN.result_check_but.setEnabled(False)
        object.AUTO_DETECTION_WIN.back_next_but.setEnabled(False)
        object.AUTO_DETECTION_WIN.detect_but.setEnabled(False)

    # 继续检测
    def continue_detect(self):
        self.action_clean_back()
        object.AUTO_DETECTION_WIN.stackedWidget.setCurrentIndex(0)

    # 复制
    def action_copy(self):
        self.copy_board.setText(object.AUTO_DETECTION_WIN.product_id_text.text())
        QMessageBox.information(object.AUTO_DETECTION_QWIDGET, "Attention", "Copy successful")

    # 退出窗口
    def action_exit(self):
        self.reset_window()
        object.AUTO_DETECTION_QWIDGET.close()
        object.DETECTION_QWIDGET.show()

    # 重置路径
    def action_reset_path(self):
        object.AUTO_DETECTION_WIN.target_path.clear()
        object.AUTO_DETECTION_WIN.result_path.clear()
        object.AUTO_DETECTION_WIN.reset_but.setEnabled(False)
        object.AUTO_DETECTION_WIN.target_path.setEnabled(True)
        object.AUTO_DETECTION_WIN.result_path.setEnabled(True)
        object.AUTO_DETECTION_WIN.files_num.clear()
        object.AUTO_DETECTION_WIN.imgs_type.clear()
        object.AUTO_DETECTION_WIN.confirm_but.setEnabled(True)
        object.AUTO_DETECTION_WIN.result_path.setPlainText('batch_detect/')

    # 切换上一个数据
    def last_data_show(self):
        if int(object.AUTO_DETECTION_WIN.current_lcd.value()) > 1:
            lcd_index = int(object.AUTO_DETECTION_WIN.current_lcd.value())
            object.AUTO_DETECTION_WIN.current_lcd.display(lcd_index - 1)
            self.result_show(int(object.AUTO_DETECTION_WIN.current_lcd.value()) - 1)
            if int(object.AUTO_DETECTION_WIN.current_lcd.value()) - 1 < len(self.df_set) - 1:
                object.AUTO_DETECTION_WIN.next_page_but.setEnabled(True)
        if int(object.AUTO_DETECTION_WIN.current_lcd.value()) - 1 < 1:
            object.AUTO_DETECTION_WIN.previous_but.setEnabled(False)

    # 切换下一个数据
    def next_data_show(self):
        if int(object.AUTO_DETECTION_WIN.current_lcd.value()) - 1 < len(self.df_set) - 1:
            lcd_index = int(object.AUTO_DETECTION_WIN.current_lcd.value())
            object.AUTO_DETECTION_WIN.current_lcd.display(lcd_index + 1)
            self.result_show(int(object.AUTO_DETECTION_WIN.current_lcd.value()) - 1)
            if int(object.AUTO_DETECTION_WIN.current_lcd.value()) > 0:
                object.AUTO_DETECTION_WIN.previous_but.setEnabled(True)
        if int(object.AUTO_DETECTION_WIN.current_lcd.value()) > len(self.df_set) - 1:
            object.AUTO_DETECTION_WIN.next_page_but.setEnabled(False)

    # 结果显示
    def result_show(self, index):
        self.show_imgs(object.AUTO_DETECTION_WIN.org_view, self.df_set[index]['org_address'])
        self.show_imgs(object.AUTO_DETECTION_WIN.res_view, self.df_set[index]['res_address'])
        object.AUTO_DETECTION_WIN.img_size_text.setText(self.df_set[index]['img_size'])

        object.AUTO_DETECTION_WIN.img_name_text.setText(self.df_set[index]['img_name'])
        object.AUTO_DETECTION_WIN.img_type_text.setText(self.df_set[index]['img_type'])

        tmp_values = ast.literal_eval(self.df_set[index]['defect_num'])
        for i in range(len(tmp_values)):
            if tmp_values[i] == ' ':
                tmp_values[i] = '0'
        object.AUTO_DETECTION_WIN.num_1.setText(tmp_values[0])
        object.AUTO_DETECTION_WIN.num_2.setText(tmp_values[1])
        object.AUTO_DETECTION_WIN.num_3.setText(tmp_values[2])
        object.AUTO_DETECTION_WIN.num_4.setText(tmp_values[3])
        object.AUTO_DETECTION_WIN.num_5.setText(tmp_values[4])
        object.AUTO_DETECTION_WIN.num_6.setText(tmp_values[5])

        object.AUTO_DETECTION_WIN.result_text.setText(self.df_set[index]['final_result'])
        object.AUTO_DETECTION_WIN.product_id_text.setText(self.df_set[index]['product_id'])


    # 检测结果查看和更新第一张数据
    def action_batch_result_review(self):
        object.AUTO_DETECTION_WIN.stackedWidget.setCurrentIndex(1)
        d_set = requests.post("http://127.0.0.1:5050/batch_result")
        self.df_set = ast.literal_eval(d_set.json().get('set'))
        object.AUTO_DETECTION_WIN.total_lcd.display(len(self.df_set))
        object.AUTO_DETECTION_WIN.current_lcd.display(1)
        object.AUTO_DETECTION_WIN.img_size_text.setText(self.df_set[0]['img_size'])
        self.result_show(int(object.AUTO_DETECTION_WIN.current_lcd.value()) - 1)

        for i in range(len(self.df_set)):
            print(self.df_set[i])


    # 计算图片数量和类型
    def action_count_imgs(self):
        # 有效图像数量
        count = 0
        # 图像类型
        types = []
        # 整合图像类型
        types_text = ""
        for root, dirs, files in os.walk(object.AUTO_DETECTION_WIN.target_path.toPlainText()):
            for i in files:
                if i.split('.')[len(i.split('.')) - 1] in self.regular:
                    count += 1
                if i.split('.')[len(i.split('.')) - 1] not in types:
                    types.append(i.split('.')[len(i.split('.')) - 1])
        object.AUTO_DETECTION_WIN.files_num.setText(str(count))
        for j in types:
            types_text += j
            types_text += ','
        object.AUTO_DETECTION_WIN.imgs_type.setText(types_text.strip(','))

    # 显示图片
    def show_imgs(self, view, img_path):
        pix_map = QPixmap(img_path)
        item = QGraphicsPixmapItem(pix_map)
        scene = QGraphicsScene()
        scene.addItem(item)
        scene.setSceneRect(item.boundingRect())
        view.setScene(scene)
        view.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)

    # 确认文件路径
    def action_confirm_path(self):
        if len(object.AUTO_DETECTION_WIN.target_path.toPlainText()) == 0 or len(object.AUTO_DETECTION_WIN.result_path.toPlainText()) == 0:
            QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", "Path is empty !")
            return

        self.path_set = {"target":object.AUTO_DETECTION_WIN.target_path.toPlainText(),"result":object.AUTO_DETECTION_WIN.result_path.toPlainText()}
        response_path = requests.post("http://127.0.0.1:5050/batch_detect_path", json=self.path_set)
        if response_path.json().get('status') != 'pass':
            QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", response_path.json().get('infor'))
            self.path_set.clear()
            return

        object.AUTO_DETECTION_WIN.confirm_but.setEnabled(False)
        object.AUTO_DETECTION_WIN.reset_but.setEnabled(True)
        object.AUTO_DETECTION_WIN.detect_but.setEnabled(True)
        object.AUTO_DETECTION_WIN.target_path.setEnabled(False)
        object.AUTO_DETECTION_WIN.result_path.setEnabled(False)
        self.action_count_imgs()

    # 更新进度条
    def dynamic_update(self):
        if object.AUTO_DETECTION_WIN.status_progressBar.value() < 100:
            object.AUTO_DETECTION_WIN.status_progressBar.setValue(object.AUTO_DETECTION_WIN.status_progressBar.value() + int(self.update_interval))

    # 开始检测
    def action_detect(self):
        object.AUTO_DETECTION_WIN.tabWidget.setTabEnabled(0, False)
        object.AUTO_DETECTION_WIN.tabWidget.setCurrentIndex(1)
        object.AUTO_DETECTION_WIN.tabWidget.setTabEnabled(1, True)
        # 计算实时进度条间隔数
        self.update_interval = 100 / eval(object.AUTO_DETECTION_WIN.files_num.text())

        for root, dirs, files in os.walk(object.AUTO_DETECTION_WIN.target_path.toPlainText()):
            for i in files:
                if i.split('.')[len(i.split('.')) - 1] in self.regular:
                    img_file = {"file_path":root + '\\' + i,"output_path":object.AUTO_DETECTION_WIN.result_path.toPlainText()}
                    response_detect = requests.post("http://127.0.0.1:5050/batch_detect", json=img_file)
                    if response_detect.json().get('status') != 'pass':
                        QMessageBox.warning(object.REGISTER_QWIDGET, "Attention", response_detect.json().get('infor'))
                        return
                    self.dynamic_update()

        if object.AUTO_DETECTION_WIN.status_progressBar.value() < 100:
            object.AUTO_DETECTION_WIN.status_progressBar.setValue(100)

        object.AUTO_DETECTION_WIN.status_label.setText("Detection completed !")
        object.AUTO_DETECTION_WIN.result_check_but.setEnabled(True)
        object.AUTO_DETECTION_WIN.back_next_but.setEnabled(True)



    # 返回主界面
    def action_back(self):
        object.DETECTION_QWIDGET.show()
        object.AUTO_DETECTION_QWIDGET.hide()
        self.reset_window()
